from db import get_pg_connector
from main import get_args

def get_all_tables() -> str:
    """
    Returns list of tables in the DB
    """
    query = """
          SELECT table_name AS tn
          FROM information_schema.tables
          WHERE table_schema = 'public';
          """
    pg_connector = get_pg_connector()
    res = pg_connector.fetch_all(query)
    print(res)
    return " ".join([el["tn"] for el in res])

if __name__ == "__main__":
    args = get_args()
    db_params = {
        "host": args.db_host,
        "port": args.db_port,
        "user": args.db_user,
        "password": args.db_password,
        "dbname": args.db_name,
    }
    _= get_pg_connector(db_params)
    t = get_all_tables()
    print(t)
