"""Database connection and session management."""

DB_URL = "postgresql://localhost:5432/appdb"
POOL_SIZE = 5


def init_db():
    """Initialize the database connection pool."""
    import sqlalchemy
    engine = sqlalchemy.create_engine(DB_URL, pool_size=POOL_SIZE)
    return engine


def get_session(engine):
    """Return a new database session."""
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    return Session()
