import sqlite3


DB_PATH = "database/business.db"


def calculate_kpis(start_date: str, end_date: str):
    """Calcola i principali KPI per un periodo."""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            SUM(oi.quantity * oi.unit_price) AS revenue,
            SUM(oi.quantity * oi.unit_cost) AS cost,
            SUM(
                oi.quantity * (oi.unit_price - oi.unit_cost)
            ) AS gross_profit,
            COUNT(DISTINCT o.order_id) AS orders
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        WHERE o.order_date BETWEEN ? AND ?
        """,
        (start_date, end_date)
    )

    result = cursor.fetchone()
    conn.close()

    revenue = result[0] or 0
    cost = result[1] or 0
    gross_profit = result[2] or 0
    orders = result[3] or 0

    gross_margin = gross_profit / revenue if revenue > 0 else 0
    average_order_value = revenue / orders if orders > 0 else 0

    return {
        "revenue": revenue,
        "cost": cost,
        "gross_profit": gross_profit,
        "gross_margin": gross_margin,
        "orders": orders,
        "average_order_value": average_order_value
    }