import sqlite3
from datetime import datetime


DB_PATH = "database/business.db"


def save_investigation(
    country,
    metric,
    previous_value,
    current_value,
    change,
    report
):
    """
    Salva nel database il risultato
    di un'investigazione dell'agente.
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO investigations (
            created_at,
            country,
            metric,
            previous_value,
            current_value,
            change,
            report,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(),
            country,
            metric,
            previous_value,
            current_value,
            change,
            report,
            "open"
        )
    )

    conn.commit()
    conn.close()