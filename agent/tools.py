import sqlite3

from analytics.anomalies import detect_anomalies


DB_PATH = "database/business.db"


def query_database(sql: str):
    """
    Esegue query SQL di sola lettura sul database aziendale.

    Usa questo tool per recuperare dati necessari
    alle analisi di business.
    """

    clean_sql = sql.strip()
    upper_sql = clean_sql.upper()

    # Deve essere una SELECT
    if not upper_sql.startswith("SELECT"):
        return {
            "error": "Sono consentite solamente query SELECT."
        }

    # Blocchiamo istruzioni pericolose
    forbidden = [
        "DELETE",
        "DROP",
        "UPDATE",
        "INSERT",
        "ALTER",
        "CREATE",
        "REPLACE",
        "TRUNCATE",
        "ATTACH",
        "DETACH",
        "PRAGMA"
    ]

    for keyword in forbidden:

        if keyword in upper_sql:
            return {
                "error": (
                    f"Query bloccata: "
                    f"operazione {keyword} non consentita."
                )
            }

    # Permettiamo una sola istruzione SQL
    if ";" in clean_sql[:-1]:
        return {
            "error": "È consentita una sola query alla volta."
        }

    try:

        # Database aperto in modalità read-only
        conn = sqlite3.connect(
            f"file:{DB_PATH}?mode=ro",
            uri=True
        )

        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute(clean_sql)

        # Massimo 200 righe restituite
        rows = cursor.fetchmany(200)

        result = [
            dict(row)
            for row in rows
        ]

        conn.close()

        return {
            "rows": result,
            "returned_rows": len(result)
        }

    except Exception as error:

        return {
            "error": str(error)
        }


def monitor_business():
    """
    Analizza automaticamente il business
    e restituisce le anomalie rilevate.
    """

    anomalies = detect_anomalies()

    if not anomalies:
        return {
            "status": "ok",
            "message": "Nessuna anomalia significativa rilevata."
        }

    return {
        "status": "anomalies_detected",
        "anomalies": anomalies
    }