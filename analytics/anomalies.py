import sqlite3


DB_PATH = "database/business.db"

PREVIOUS_START = "2026-04-01"
PREVIOUS_END = "2026-06-30"

CURRENT_START = "2026-07-01"
CURRENT_END = "2026-09-30"


def detect_anomalies():

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    anomalies = []

    # Dimensioni singole + combinazioni
    dimensions = {
        "country": ["c.country"],
        "channel": ["o.channel"],
        "segment": ["c.segment"],
        "product": ["p.product_name"],
        "category": ["p.category"],

        "country_channel": [
            "c.country",
            "o.channel"
        ],

        "country_segment": [
            "c.country",
            "c.segment"
        ],

        "country_product": [
            "c.country",
            "p.product_name"
        ],

        "country_category": [
            "c.country",
            "p.category"
        ]
    }


    for dimension_name, columns in dimensions.items():

        select_columns = ", ".join(columns)
        group_columns = ", ".join(columns)

        query = f"""
        SELECT
            {select_columns},

            SUM(
                CASE
                    WHEN o.order_date BETWEEN ? AND ?
                    THEN oi.quantity * oi.unit_price
                    ELSE 0
                END
            ) AS previous_revenue,

            SUM(
                CASE
                    WHEN o.order_date BETWEEN ? AND ?
                    THEN oi.quantity * oi.unit_price
                    ELSE 0
                END
            ) AS current_revenue,

            SUM(
                CASE
                    WHEN o.order_date BETWEEN ? AND ?
                    THEN oi.quantity *
                    (oi.unit_price - oi.unit_cost)
                    ELSE 0
                END
            ) AS previous_profit,

            SUM(
                CASE
                    WHEN o.order_date BETWEEN ? AND ?
                    THEN oi.quantity *
                    (oi.unit_price - oi.unit_cost)
                    ELSE 0
                END
            ) AS current_profit,

            COUNT(
                DISTINCT CASE
                    WHEN o.order_date BETWEEN ? AND ?
                    THEN o.order_id
                END
            ) AS previous_orders,

            COUNT(
                DISTINCT CASE
                    WHEN o.order_date BETWEEN ? AND ?
                    THEN o.order_id
                END
            ) AS current_orders,

            COUNT(
                DISTINCT CASE
                    WHEN o.order_date BETWEEN ? AND ?
                    THEN o.customer_id
                END
            ) AS previous_customers,

            COUNT(
                DISTINCT CASE
                    WHEN o.order_date BETWEEN ? AND ?
                    THEN o.customer_id
                END
            ) AS current_customers

        FROM orders o

        JOIN customers c
            ON o.customer_id = c.customer_id

        JOIN order_items oi
            ON o.order_id = oi.order_id

        JOIN products p
            ON oi.product_id = p.product_id

        GROUP BY {group_columns}
        """

        params = (
            PREVIOUS_START, PREVIOUS_END,
            CURRENT_START, CURRENT_END,

            PREVIOUS_START, PREVIOUS_END,
            CURRENT_START, CURRENT_END,

            PREVIOUS_START, PREVIOUS_END,
            CURRENT_START, CURRENT_END,

            PREVIOUS_START, PREVIOUS_END,
            CURRENT_START, CURRENT_END
        )

        rows = conn.execute(
            query,
            params
        ).fetchall()


        for row in rows:

            # Valori della dimensione
            dimension_values = [
                row[column.split(".")[-1]]
                for column in columns
            ]

            value = " | ".join(
                str(v)
                for v in dimension_values
            )

            previous_revenue = (
                row["previous_revenue"] or 0
            )

            current_revenue = (
                row["current_revenue"] or 0
            )

            previous_profit = (
                row["previous_profit"] or 0
            )

            current_profit = (
                row["current_profit"] or 0
            )

            previous_orders = (
                row["previous_orders"] or 0
            )

            current_orders = (
                row["current_orders"] or 0
            )

            previous_customers = (
                row["previous_customers"] or 0
            )

            current_customers = (
                row["current_customers"] or 0
            )


            # Evitiamo segmenti troppo piccoli
            if previous_orders < 20:
                continue


            # =============================================
            # REVENUE
            # =============================================

            if previous_revenue > 0:

                change = (
                    current_revenue
                    - previous_revenue
                ) / previous_revenue

                if abs(change) >= 0.25:

                    anomalies.append({
                        "dimension": dimension_name,
                        "value": value,
                        "metric": "revenue",
                        "previous": previous_revenue,
                        "current": current_revenue,
                        "change": change,
                        "anomaly_score": abs(change)
                    })


            # =============================================
            # ORDERS
            # =============================================

            if previous_orders > 0:

                change = (
                    current_orders
                    - previous_orders
                ) / previous_orders

                if abs(change) >= 0.25:

                    anomalies.append({
                        "dimension": dimension_name,
                        "value": value,
                        "metric": "orders",
                        "previous": previous_orders,
                        "current": current_orders,
                        "change": change,
                        "anomaly_score": abs(change)
                    })


            # =============================================
            # ACTIVE CUSTOMERS
            # =============================================

            if previous_customers >= 20:

                change = (
                    current_customers
                    - previous_customers
                ) / previous_customers

                if abs(change) >= 0.25:

                    anomalies.append({
                        "dimension": dimension_name,
                        "value": value,
                        "metric": "active_customers",
                        "previous": previous_customers,
                        "current": current_customers,
                        "change": change,
                        "anomaly_score": abs(change)
                    })


            # =============================================
            # GROSS MARGIN
            # =============================================

            if (
                previous_revenue > 0
                and current_revenue > 0
            ):

                previous_margin = (
                    previous_profit
                    / previous_revenue
                )

                current_margin = (
                    current_profit
                    / current_revenue
                )

                margin_change = (
                    current_margin
                    - previous_margin
                )

                if abs(margin_change) >= 0.03:

                    # Per rendere confrontabile lo score:
                    # 5pp = score 0.50
                    anomaly_score = (
                        abs(margin_change) * 10
                    )

                    anomalies.append({
                        "dimension": dimension_name,
                        "value": value,
                        "metric": "gross_margin",
                        "previous": previous_margin,
                        "current": current_margin,
                        "change": margin_change,
                        "anomaly_score": anomaly_score
                    })


    conn.close()

    # Le anomalie più forti vengono prima
    anomalies.sort(
        key=lambda x: x["anomaly_score"],
        reverse=True
    )

    return anomalies