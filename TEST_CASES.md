# Graph Augmentation Test Cases — v2

Three commits on `main`, two merged PRs, one intentionally unmerged branch.

- Entity resolution: **exact symbol names only** (filename, function, global variable).
- Invalidation: **PR body vs PR comment only**. No README parsing.
- Version-aware edges: references in a PR must point to the CodeNodeVersion at
  **that PR's commit SHA**, not HEAD.
- Negative test: symbols on unmerged branches must not appear in the graph.

---

## Repo layout (post-merge)

```
src/
  db.py      — DB_URL, POOL_SIZE, CONNECTION_TIMEOUT (globals)
               init_db(), get_session() (functions)
  auth.py    — SECRET_KEY, TOKEN_TTL_HOURS (globals)
               generate_token(), verify_token() (functions)
  tasks.py   — MAX_RETRIES, RETRY_DELAY_SECONDS (globals)
               create_task(), delete_task(), retry_task() (functions)
  config.py  — APP_PORT, DEBUG_MODE (globals)
               load_config() (function)
tests/
  test_db.py
  test_auth.py
```

Branch `feature/add-query-cache` — open PR, **never merged**:
```
src/cache.py — CACHE_TTL_SECONDS (global), cache_query(), get_cached() (functions)
```

---

## Category A — Entity Resolution

Exact name matching. Each test gives the source text and the expected node.

### TC-01 — Function name in PR body → function node
**Source**: PR #1 body
**Trigger text**: `` `init_db()` in `db.py` ``
**Expected edge**: `PR#1 --[REFERENCES]--> FunctionNode(init_db, src/db.py)`
**Hard failure**: pipeline creates a new floating node for `init_db` instead of
matching the existing function node; or resolves only to the file node `db.py`.

---

### TC-02 — Global variable name in PR body → global var node
**Source**: PR #1 body
**Trigger text**: `` `DB_URL` in `db.py` ``
**Expected edge**: `PR#1 --[REFERENCES]--> GlobalVarNode(DB_URL, src/db.py)`
**Hard failure**: resolves to file node `db.py` rather than the `DB_URL` var node.

---

### TC-03 — Global variable + filename in PR comment → var node in correct file
**Source**: PR #1 comment
**Trigger text**: `` `MAX_RETRIES` in `tasks.py` ``
**Expected edge**: `PR#1-comment --[REFERENCES]--> GlobalVarNode(MAX_RETRIES, src/tasks.py)`
**Hard failure**: resolves to file node `tasks.py` instead of `MAX_RETRIES`;
or creates a duplicate node.

---

### TC-04 — Global variable + filename in PR body → var node in correct file
**Source**: PR #2 body
**Trigger text**: `` `SECRET_KEY` in `auth.py` ``
**Expected edge**: `PR#2 --[REFERENCES]--> GlobalVarNode(SECRET_KEY, src/auth.py)`
**Hard failure**: resolves to file node `auth.py` or wrong file.

---

### TC-05 — Global variable + filename in PR body → var node (different file)
**Source**: PR #2 body
**Trigger text**: `` `APP_PORT` in `config.py` ``
**Expected edge**: `PR#2 --[REFERENCES]--> GlobalVarNode(APP_PORT, src/config.py)`
**Hard failure**: resolves to `SECRET_KEY` (wrong symbol) or to `config.py` file node.

---

### TC-ERR-01 — Symbol from unmerged branch must NOT be resolved
**Source**: PR #3 (unmerged) body
**Trigger text**: `` `cache_query()` `` and `` `CACHE_TTL_SECONDS` ``
**Expected**: NO nodes exist for `cache_query`, `get_cached`, `CACHE_TTL_SECONDS`,
or `src/cache.py` after ingesting `main`.
**Hard failure**: pipeline indexes commits from open/unmerged branches and creates
nodes for symbols that do not exist on `main`.

---

## Category B — Version-Aware Edges

A reference in PR #N should link to the file's state **at PR #N's merge commit**,
not at HEAD. This verifies the pipeline tracks CodeNodeVersions per commit SHA.

### TC-06 — Reference + modification in same PR → edge to that commit's version
**Setup**: PR #1 body references `init_db()` AND PR #1's commit modifies `db.py`.
**Expected**:
```
FunctionNode(init_db) --[AT_VERSION]--> CodeNodeVersion(src/db.py, sha=<PR1-merge-sha>)
```
**Hard failure**: edge points to `src/db.py` at HEAD (the latest commit SHA) rather
than the commit introduced by PR #1.

---

### TC-07 — Comment reference + modification in same PR → correct version
**Setup**: PR #1 comment references `MAX_RETRIES in tasks.py` AND PR #1's commit
modifies `tasks.py` (bumping it from 3 to 5).
**Expected**:
```
GlobalVarNode(MAX_RETRIES) --[AT_VERSION]--> CodeNodeVersion(src/tasks.py, sha=<PR1-merge-sha>)
```
At this version, `MAX_RETRIES = 5`.
**Hard failure**: edge points to the initial commit version where `MAX_RETRIES = 3`.

---

### TC-08 — File NOT modified in a PR → no new CodeNodeVersion created for it
**Setup**: PR #2 modifies `auth.py` and `config.py` but does NOT touch `tasks.py`.
**Expected**: No `CodeNodeVersion(src/tasks.py, sha=<PR2-merge-sha>)` node is
created. The latest version of `tasks.py` remains at `<PR1-merge-sha>`.
**Hard failure**: pipeline creates a spurious new version node for every file on
every PR merge, even for files that were not changed.

---

## Category C — Temporal Invalidation

Invalidation lives only in PR bodies and PR comments. The two facts must clearly
reference the same symbol and directly contradict each other.

### TC-09 — PR comment directly invalidates a fact stated in the PR body
**Source**: PR #2

**Fact A — from PR body (initially ACTIVE)**:
> "The `APP_PORT` change was necessary because port 8080 was blocked by the corporate firewall."

**Fact B — from PR comment (should INVALIDATE Fact A)**:
> "Correction: the `APP_PORT` change from 8080 to 9000 in `config.py` was caused
> by a load balancer misconfiguration that permanently bound port 8080 to a
> different service — not a firewall block."

**Expected final state**:
```
ACTIVE:      Fact B  — "APP_PORT changed due to load balancer misconfiguration"
INVALIDATED: Fact A  — "APP_PORT changed because firewall blocked port 8080"
```
Both facts linked to `GlobalVarNode(APP_PORT, src/config.py)`.

**Hard failure A**: both Fact A and Fact B are simultaneously ACTIVE.
**Hard failure B**: Fact A remains ACTIVE; Fact B is ignored.
**Hard failure C**: neither fact is linked to the `APP_PORT` node.

**Invalidation signal**: comment begins with "Correction:" and references the same
symbol (`APP_PORT`) and file (`config.py`) as the body, asserting a different
causal reason for the same observed change.

---

## Category D — Negative Test

### TC-10 — No nodes from unmerged branch appear in the graph
**Branch**: `feature/add-query-cache` — open PR, never merged to `main`.
**Symbols that must NOT appear as graph nodes**:
- `FunctionNode(cache_query, src/cache.py)`
- `FunctionNode(get_cached, src/cache.py)`
- `GlobalVarNode(CACHE_TTL_SECONDS, src/cache.py)`
- `FileNode(src/cache.py)`

**Verification query**: after full ingestion of `main`, query for any node whose
source path contains `cache.py`. The result set must be empty.

**Hard failure**: pipeline walks all branches (not just `main`) and creates nodes
for symbols in work-in-progress code that was intentionally never merged.

---

## Summary Table

| ID        | Category          | Source         | Symbol                     | Expected result                        |
|-----------|-------------------|----------------|----------------------------|----------------------------------------|
| TC-01     | Entity Resolution | PR#1 body      | `init_db()`                | FunctionNode in db.py                  |
| TC-02     | Entity Resolution | PR#1 body      | `DB_URL` in db.py          | GlobalVarNode in db.py                 |
| TC-03     | Entity Resolution | PR#1 comment   | `MAX_RETRIES` in tasks.py  | GlobalVarNode in tasks.py              |
| TC-04     | Entity Resolution | PR#2 body      | `SECRET_KEY` in auth.py    | GlobalVarNode in auth.py               |
| TC-05     | Entity Resolution | PR#2 body      | `APP_PORT` in config.py    | GlobalVarNode in config.py             |
| TC-ERR-01 | Entity Resolution | PR#3 (unmerged)| `cache_query()`            | Must NOT exist in graph                |
| TC-06     | Version-Aware     | PR#1           | init_db() + db.py modified | Edge → db.py@PR1-sha                   |
| TC-07     | Version-Aware     | PR#1 comment   | MAX_RETRIES + tasks.py mod | Edge → tasks.py@PR1-sha (value=5)      |
| TC-08     | Version-Aware     | PR#2           | tasks.py NOT modified      | No new CodeNodeVersion for tasks.py    |
| TC-09     | Invalidation      | PR#2 body+comment | APP_PORT in config.py   | Comment invalidates body fact          |
| TC-10     | Negative Test     | Unmerged branch| cache_query(), cache.py    | Must NOT appear in graph               |

---

## Scoring

- **PASS**: assertion holds exactly.
- **SOFT FAIL**: right node type but wrong edge (e.g. points to HEAD instead of PR SHA).
- **HARD FAIL**: wrong node created, contradiction both active, or unmerged symbol indexed.

MVP target: **0 HARD FAILs**.
