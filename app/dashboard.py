import sys
import sqlite3
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))


from analytics.kpi import calculate_kpis
from analytics.anomalies import detect_country_anomalies
from analytics.dashboard_data import (
    get_monthly_performance,
    get_country_performance
)
from agent.agent import ask_agent


DB_PATH = "database/business.db"


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="AI Business Analyst",
    page_icon="📊",
    layout="wide"
)


st.title("AI Business Analyst")

st.caption(
    "Autonomous monitoring, anomaly detection "
    "and AI-powered root-cause analysis"
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Business Overview",
        "AI Analyst",
        "Investigations"
    ]
)


# =========================================================
# BUSINESS OVERVIEW
# =========================================================

if page == "Business Overview":

    st.header("Business Overview")

    current = calculate_kpis(
        "2026-07-01",
        "2026-09-30"
    )

    previous = calculate_kpis(
        "2026-04-01",
        "2026-06-30"
    )


    def percentage_change(current_value, previous_value):

        if previous_value == 0:
            return 0

        return (
            (current_value - previous_value)
            / previous_value
        )


    revenue_change = percentage_change(
        current["revenue"],
        previous["revenue"]
    )

    orders_change = percentage_change(
        current["orders"],
        previous["orders"]
    )

    margin_change = (
        current["gross_margin"]
        - previous["gross_margin"]
    )


    # KPI CARDS

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Revenue",
        f"€{current['revenue']:,.0f}",
        f"{revenue_change:+.1%}"
    )

    col2.metric(
        "Gross Margin",
        f"{current['gross_margin']:.1%}",
        f"{margin_change:+.1%}"
    )

    col3.metric(
        "Orders",
        f"{current['orders']:,}",
        f"{orders_change:+.1%}"
    )

    col4.metric(
        "Average Order Value",
        f"€{current['average_order_value']:,.0f}"
    )


    # MONTHLY PERFORMANCE

    st.divider()

    st.subheader("Monthly Revenue")

    monthly = get_monthly_performance()

    st.line_chart(
        monthly,
        x="month",
        y="revenue"
    )


    st.subheader("Monthly Gross Margin")

    st.line_chart(
        monthly,
        x="month",
        y="gross_margin"
    )


    # COUNTRY PERFORMANCE

    st.divider()

    st.subheader("Country Performance")

    countries = get_country_performance()

    st.dataframe(
        countries,
        use_container_width=True,
        hide_index=True
    )


    # ANOMALIES

    st.divider()

    st.subheader("Detected Anomalies")

    anomalies = detect_country_anomalies()

    if not anomalies:

        st.success(
            "No significant anomalies detected."
        )

    else:

        for anomaly in anomalies:

            st.warning(
                f"""
                **{anomaly['country']} — Gross Margin**

                Previous:
                {anomaly['previous_margin']:.1%}

                Current:
                {anomaly['current_margin']:.1%}

                Change:
                {anomaly['margin_change']:+.1%}
                """
            )


# =========================================================
# AI ANALYST
# =========================================================

elif page == "AI Analyst":

    st.header("Ask AI Analyst")

    st.write(
        """
        Ask questions about revenue, margins,
        products, countries, channels or customers.
        The agent can autonomously query the database
        to investigate your question.
        """
    )

    question = st.text_area(
        "Business question",
        placeholder=(
            "Why did gross margin decline "
            "in Spain?"
        )
    )

    if st.button(
        "Run Investigation",
        type="primary"
    ):

        if question:

            with st.spinner(
                "AI Analyst is investigating the data..."
            ):

                answer = ask_agent(question)

            st.markdown(answer)

        else:

            st.warning(
                "Enter a question first."
            )


# =========================================================
# INVESTIGATION HISTORY
# =========================================================

elif page == "Investigations":

    st.header("Investigation History")

    conn = sqlite3.connect(DB_PATH)

    try:

        investigations = conn.execute(
            """
            SELECT
                investigation_id,
                created_at,
                country,
                metric,
                previous_value,
                current_value,
                change,
                report,
                status

            FROM investigations

            ORDER BY investigation_id DESC
            """
        ).fetchall()

    except sqlite3.OperationalError:

        investigations = []

    conn.close()


    if not investigations:

        st.info(
            "No investigations have been saved yet."
        )

    else:

        for investigation in investigations:

            (
                investigation_id,
                created_at,
                country,
                metric,
                previous_value,
                current_value,
                change,
                report,
                status
            ) = investigation


            with st.expander(
                f"#{investigation_id} — "
                f"{country} — {metric}"
            ):

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Previous",
                    f"{previous_value:.1%}"
                )

                col2.metric(
                    "Current",
                    f"{current_value:.1%}"
                )

                col3.metric(
                    "Change",
                    f"{change:+.1%}"
                )

                st.write(
                    f"**Status:** {status}"
                )

                st.write(
                    f"**Created:** {created_at}"
                )

                st.divider()

                st.markdown(report)