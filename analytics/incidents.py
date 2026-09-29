from analytics.anomalies import detect_anomalies


def build_incidents():
    """
    Raggruppa anomalie correlate in incidenti di business.

    Le anomalie vengono raggruppate principalmente
    per area geografica, indipendentemente dalla metrica.
    """

    anomalies = detect_anomalies()

    incident_groups = {}

    for anomaly in anomalies:

        value = anomaly["value"]

        # Se abbiamo "Spain | Laptop Pro",
        # il contesto principale è "Spain".
        primary_context = value.split(" | ")[0]

        if primary_context not in incident_groups:
            incident_groups[primary_context] = []

        incident_groups[primary_context].append(anomaly)


    incidents = []

    for context, signals in incident_groups.items():

        # Segnale più forte del gruppo
        primary = max(
            signals,
            key=lambda x: x["anomaly_score"]
        )

        # Score complessivo:
        # usiamo il segnale più forte come priorità principale
        incident_score = primary["anomaly_score"]

        # Metriche coinvolte
        metrics = sorted(
            set(
                signal["metric"]
                for signal in signals
            )
        )

        incidents.append({
            "context": context,
            "primary": primary,
            "related_signals": signals,
            "metrics": metrics,
            "signal_count": len(signals),
            "incident_score": incident_score
        })


    incidents.sort(
        key=lambda x: x["incident_score"],
        reverse=True
    )

    return incidents