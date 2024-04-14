from config.db import DB_SCHEME, DB_HOST, DB_PORT


def get_db_uri():
    return f"{DB_SCHEME}://{DB_HOST}:{DB_PORT}"
