from analytics.incidents import build_incidents
from agent.agent import ask_agent
from database.investigations import save_investigation


MAX_INCIDENTS = 3


def run_monitor():

    incidents = build_incidents()

    if not incidents:
        print("Nessun incidente significativo rilevato.")
        return

    top_incidents = incidents[:MAX_INCIDENTS]

    print(
        f"\nRilevati {len(incidents)} incidenti."
        f"\nInvestigo automaticamente i {len(top_incidents)} più importanti."
    )

    for incident in top_incidents:

        context = incident["context"]
        primary = incident["primary"]
        signals = incident["related_signals"]

        signals_text = "\n".join(
            [
                (
                    f"- Dimension: {signal['dimension']} | "
                    f"Value: {signal['value']} | "
                    f"Metric: {signal['metric']} | "
                    f"Previous: {signal['previous']} | "
                    f"Current: {signal['current']} | "
                    f"Change: {signal['change']:.2%}"
                )
                for signal in signals
            ]
        )

        prompt = f"""
You are investigating an automatically detected business incident.

BUSINESS CONTEXT:
{context}

PRIMARY SIGNAL:
Dimension: {primary['dimension']}
Value: {primary['value']}
Metric: {primary['metric']}
Change: {primary['change']:.2%}

OTHER RELATED SIGNALS:
{signals_text}

Investigate autonomously using the SQL database.

Do not simply repeat the anomaly detector output.

Use SQL to determine:

- when the change started
- which underlying dimension is driving it
- whether the signals share the same driver
- whether this is a real deterioration, improvement, or mix shift
- the most likely root cause that is directly supported by the data

Continue investigating until you have enough evidence.

Final answer structure:

1. DATA EVIDENCE
2. INTERPRETATION
3. ROOT CAUSE SUPPORTED BY DATA
4. BUSINESS IMPACT
5. HYPOTHESES REQUIRING ADDITIONAL DATA

Never present an unsupported hypothesis as fact.
"""

        print("\n" + "=" * 70)
        print(f"INVESTIGATING INCIDENT: {context}")
        print("=" * 70)

        result = ask_agent(prompt)

        print("\n" + result)

        save_investigation(
            country=context,
            metric=primary["metric"],
            previous_value=primary["previous"],
            current_value=primary["current"],
            change=primary["change"],
            report=result
        )