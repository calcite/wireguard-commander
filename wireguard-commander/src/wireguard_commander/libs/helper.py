import pathlib
import re
import subprocess
import duckdb
import loggate

logger = loggate.get_logger('helper')


def setup_db_connection(db_config: dict) -> duckdb.DuckDBPyConnection:
    db = duckdb.connect(db_config['path'])
    version = -1
    exist_table = db.sql(
        "SELECT count(*) FROM information_schema.tables "
        "WHERE table_name = 'db_version'"
    ).fetchone()[0]
    if exist_table > 0:
        row = db.sql(
            "SELECT version FROM db_version ORDER BY date DESC"
        ).fetchone()
        if row:
            version = int(row[0]) + 1
    try:
        for ix in range(version, 999):
            for file in pathlib.Path('./sql').glob(f'{ix}-*.sql'):
                db.begin()
                logger.info(f"Apply SQL file {file}")
                ver = re.match(r'.*/(\d+)-[^/]+$', str(file)).group(1)
                with open(file, 'r') as fd:
                    db.sql(fd.read())
                    db.sql(
                        f"INSERT INTO db_version VALUES ({int(ver)}, DEFAULT);"
                    )
                db.commit()
        return db
    except Exception as e:
        db.rollback()
        logger.error(e)
    return db


def generate_private_key():
    genkey = subprocess.Popen('wg genkey', stdout=subprocess.PIPE, shell=True)
    client_private_key, error = genkey.communicate()
    if error:
        logger.error(error)
        return None
    return client_private_key.decode("utf-8").strip()


def generate_public_key(private_key):
    echo = subprocess.Popen(f'echo {private_key}', stdout=subprocess.PIPE,
                            shell=True)
    pubkey = subprocess.Popen('wg pubkey', stdin=echo.stdout,
                              stdout=subprocess.PIPE, shell=True)
    client_public_key, error = pubkey.communicate()
    if error:
        logger.error(error)
        return None
    return client_public_key.decode("utf-8").strip()


def generate_pair_keys():
    private_key = generate_private_key()
    public_key = generate_public_key(private_key)
    return {
        'private_key': private_key,
        'public_key': public_key
    }


