import os
import json
import pyodbc
from utils import DATA_DIR, OUTPUT_DIR

def load_access_data(db_path: str, out_path: str):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")

    print(f"[INFO] Connecting to Access DB: {db_path}")
    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        f"DBQ={db_path};"
    )

    try:
        conn = pyodbc.connect(conn_str)
    except pyodbc.Error as e:
        raise ConnectionError(f"Failed to connect to Access DB: {e}")

    cursor = conn.cursor()
    tables = [t.table_name for t in cursor.tables(tableType="TABLE")]
    print(f"[INFO] Found tables: {tables}")

    docs = []
    for table in tables:
        print(f"[INFO] Reading table: {table}")
        try:
            cursor.execute(f"SELECT * FROM [{table}]")
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
        except pyodbc.Error as e:
            print(f"[WARNING] Could not read table {table}: {e}")
            continue

        for row in rows:
            row_dict = dict(zip(columns, row))
            docs.append({"table": table, "row": row_dict})

    conn.close()

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)

    print(f"[SUCCESS] Exported {len(docs)} rows to {out_path}")
    return docs

if __name__ == "__main__":
    db_path = os.path.join(DATA_DIR, "ARGO_DB_2004.accdb")
    out_path = os.path.join(OUTPUT_DIR, "argo_data.json")
    load_access_data(db_path, out_path)
