from app.config.db import DB_HOST, DB_PORT, DB_SCHEME


def get_db_uri():
    return f"{DB_SCHEME}://{DB_HOST}:{DB_PORT}"
