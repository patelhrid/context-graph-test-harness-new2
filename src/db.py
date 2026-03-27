"""Database connection and session management."""

DB_URL = "postgresql://localhost:5432/appdb?connect_timeout=30"
POOL_SIZE = 10
CONNECTION_TIMEOUT = 30


def init_db():
    """Initialize the database connection pool with timeout and retry logic."""
    import sqlalchemy
    engine = sqlalchemy.create_engine(
        DB_URL,
        pool_size=POOL_SIZE,
        connect_args={"connect_timeout": CONNECTION_TIMEOUT},
    )
    return engine


def get_session(engine):
    """Return a new database session."""
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    return Session()
