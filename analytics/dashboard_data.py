import sqlite3
import pandas as pd


DB_PATH = "database/business.db"


def get_monthly_performance():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        substr(o.order_date, 1, 7) AS month,

        SUM(
            oi.quantity * oi.unit_price
        ) AS revenue,

        SUM(
            oi.quantity * (oi.unit_price - oi.unit_cost)
        ) AS gross_profit,

        COUNT(
            DISTINCT o.order_id
        ) AS orders

    FROM orders o

    JOIN order_items oi
        ON o.order_id = oi.order_id

    GROUP BY month

    ORDER BY month
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    df["gross_margin"] = (
        df["gross_profit"]
        / df["revenue"]
    )

    return df


def get_country_performance():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        c.country,

        SUM(
            oi.quantity * oi.unit_price
        ) AS revenue,

        SUM(
            oi.quantity * (oi.unit_price - oi.unit_cost)
        ) AS gross_profit

    FROM customers c

    JOIN orders o
        ON c.customer_id = o.customer_id

    JOIN order_items oi
        ON o.order_id = oi.order_id

    WHERE o.order_date
        BETWEEN '2026-07-01'
        AND '2026-09-30'

    GROUP BY c.country

    ORDER BY revenue DESC
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    df["gross_margin"] = (
        df["gross_profit"]
        / df["revenue"]
    )

    return df