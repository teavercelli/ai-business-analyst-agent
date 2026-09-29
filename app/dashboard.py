import sys
import sqlite3
from pathlib import Path

import streamlit as st


# =========================================================
# PROJECT PATH
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))


# =========================================================
# PROJECT IMPORTS
# =========================================================

from analytics.kpi import calculate_kpis
from analytics.anomalies import detect_anomalies
from analytics.incidents import build_incidents
from analytics.dashboard_data import (
    get_monthly_performance,
    get_country_performance
)
from agent.agent import ask_agent


DB_PATH = "database/business.db"
if not Path(DB_PATH).exists():
    import database.setup

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Business Analyst",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# HEADER
# =========================================================

st.title("AI Business Analyst")

st.caption(
    "Autonomous business monitoring, anomaly detection "
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
        "Detected Incidents",
        "AI Analyst",
        "Investigation History"
    ]
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def percentage_change(current_value, previous_value):

    if previous_value == 0:
        return 0

    return (
        (current_value - previous_value)
        / previous_value
    )


def format_value(metric, value):

    if metric == "gross_margin":
        return f"{value:.1%}"

    if metric == "revenue":
        return f"€{value:,.0f}"

    if metric in [
        "orders",
        "active_customers"
    ]:
        return f"{value:,.0f}"

    return f"{value:,.2f}"


# =========================================================
# BUSINESS OVERVIEW
# =========================================================

if page == "Business Overview":

    st.header("Business Overview")

    st.caption(
        "Current period: July–September 2026 | "
        "Comparison period: April–June 2026"
    )


    # -----------------------------------------------------
    # KPI
    # -----------------------------------------------------

    current = calculate_kpis(
        "2026-07-01",
        "2026-09-30"
    )

    previous = calculate_kpis(
        "2026-04-01",
        "2026-06-30"
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


    # -----------------------------------------------------
    # MONTHLY PERFORMANCE
    # -----------------------------------------------------

    st.divider()

    st.subheader("Monthly Performance")

    monthly = get_monthly_performance()


    st.write("**Revenue Trend**")

    st.line_chart(
        monthly,
        x="month",
        y="revenue"
    )


    st.write("**Gross Margin Trend**")

    st.line_chart(
        monthly,
        x="month",
        y="gross_margin"
    )


    # -----------------------------------------------------
    # COUNTRY PERFORMANCE
    # -----------------------------------------------------

    st.divider()

    st.subheader("Country Performance")

    countries = get_country_performance()

    country_display = countries.copy()

    country_display["revenue"] = (
        country_display["revenue"]
        .map(lambda x: f"€{x:,.0f}")
    )

    country_display["gross_profit"] = (
        country_display["gross_profit"]
        .map(lambda x: f"€{x:,.0f}")
    )

    country_display["gross_margin"] = (
        country_display["gross_margin"]
        .map(lambda x: f"{x:.1%}")
    )


    st.dataframe(
        country_display,
        use_container_width=True,
        hide_index=True
    )


    # -----------------------------------------------------
    # TOP DETECTED ANOMALIES
    # -----------------------------------------------------

    st.divider()

    st.subheader("Top Detected Anomalies")

    anomalies = detect_anomalies()


    if not anomalies:

        st.success(
            "No significant anomalies detected."
        )

    else:

        for anomaly in anomalies[:5]:

            st.warning(
                f"""
**{anomaly['value']}**

Metric: **{anomaly['metric']}**

Previous: **{format_value(
    anomaly['metric'],
    anomaly['previous']
)}**

Current: **{format_value(
    anomaly['metric'],
    anomaly['current']
)}**

Change: **{anomaly['change']:+.1%}**
"""
            )


# =========================================================
# DETECTED INCIDENTS
# =========================================================

elif page == "Detected Incidents":

    st.header("Detected Business Incidents")

    st.write(
        """
        Related anomaly signals are automatically grouped
        into business incidents before AI investigation.
        """
    )


    incidents = build_incidents()


    if not incidents:

        st.success(
            "No significant business incidents detected."
        )

    else:

        for position, incident in enumerate(
            incidents[:10],
            start=1
        ):

            primary = incident["primary"]

            with st.expander(
                f"#{position} — "
                f"{incident['context']} — "
                f"{primary['metric']}"
            ):

                col1, col2, col3 = st.columns(3)


                col1.metric(
                    "Previous",
                    format_value(
                        primary["metric"],
                        primary["previous"]
                    )
                )


                col2.metric(
                    "Current",
                    format_value(
                        primary["metric"],
                        primary["current"]
                    )
                )


                col3.metric(
                    "Change",
                    f"{primary['change']:+.1%}"
                )


                st.write(
                    f"**Primary signal:** "
                    f"{primary['value']}"
                )

                st.write(
                    f"**Dimension:** "
                    f"{primary['dimension']}"
                )

                st.write(
                    f"**Related signals:** "
                    f"{incident['signal_count']}"
                )


                st.write("**Metrics involved:**")

                st.write(
                    ", ".join(
                        incident["metrics"]
                    )
                )


                st.divider()

                st.write("**Related anomaly signals**")


                for signal in incident[
                    "related_signals"
                ]:

                    st.write(
                        f"- {signal['value']} | "
                        f"{signal['metric']} | "
                        f"{signal['change']:+.1%}"
                    )


# =========================================================
# AI ANALYST
# =========================================================

elif page == "AI Analyst":

    st.header("AI Business Analyst")

    st.write(
        """
        Ask a business question in natural language.

        The AI agent can autonomously query the
        read-only SQL database to collect evidence
        and investigate the question.
        """
    )


    question = st.text_area(
        "Business question",
        placeholder=(
            "Example: Why did gross margin "
            "decline in Spain?"
        ),
        height=120
    )


    if st.button(
        "Run Investigation",
        type="primary"
    ):

        if not question:

            st.warning(
                "Enter a business question first."
            )

        else:

            with st.spinner(
                "AI Analyst is investigating the data..."
            ):

                try:

                    answer = ask_agent(
                        question
                    )

                    st.markdown(answer)

                except Exception as error:

                    st.error(
                        "The AI investigation could not "
                        "be completed."
                    )

                    st.caption(
                        "This may happen when the Gemini "
                        "free-tier API rate limit is reached."
                    )


# =========================================================
# INVESTIGATION HISTORY
# =========================================================

elif page == "Investigation History":

    st.header("Investigation History")

    st.write(
        """
        Investigations generated by the automatic
        monitoring workflow are stored here.
        """
    )


    try:

        conn = sqlite3.connect(
            DB_PATH
        )


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


        conn.close()


    except sqlite3.Error:

        investigations = []


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
                    format_value(
                        metric,
                        previous_value
                    )
                )


                col2.metric(
                    "Current",
                    format_value(
                        metric,
                        current_value
                    )
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