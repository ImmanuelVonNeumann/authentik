"""install ID"""

from functools import lru_cache
from uuid import uuid4

from psycopg import connect

from authentik.lib.config import CONFIG

# We need to string format the query as tables and schemas can't be set by parameters
# not a security issue as the config value is set by the person installing authentik
# which also has postgres credentials etc
QUERY = """SELECT id FROM {}.authentik_install_id ORDER BY id LIMIT 1;""".format(  # nosec
    CONFIG.get("postgresql.default_schema")
)


@lru_cache
def get_install_id() -> str:
    """Get install ID of this instance. The method is cached as the install ID is
    not expected to change"""
    from django.conf import settings
    from django.db import connection

    if settings.TEST:
        return str(uuid4())
    with connection.cursor() as cursor:
        cursor.execute(QUERY)
        return cursor.fetchone()[0]


@lru_cache
def get_install_id_raw():
    """Get install_id without django loaded, this is required for the startup when we get
    the install_id but django isn't loaded yet and we can't use the function above."""
    conn = connect(
        dbname=CONFIG.get("postgresql.name"),
        user=CONFIG.get("postgresql.user"),
        password=CONFIG.get("postgresql.password"),
        host=CONFIG.get("postgresql.host"),
        port=CONFIG.get_int("postgresql.port"),
        sslmode=CONFIG.get("postgresql.sslmode"),
        sslrootcert=CONFIG.get("postgresql.sslrootcert"),
        sslcert=CONFIG.get("postgresql.sslcert"),
        sslkey=CONFIG.get("postgresql.sslkey"),
    )
    cursor = conn.cursor()
    cursor.execute(QUERY)
    return cursor.fetchone()[0]
