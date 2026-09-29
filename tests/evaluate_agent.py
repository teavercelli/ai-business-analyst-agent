from analytics.anomalies import detect_anomalies


def run_evaluation():

    anomalies = detect_anomalies()

    print("\nANOMALY DETECTION EVALUATION")
    print("=" * 60)

    tests = {
        "Spain Laptop Pro margin deterioration": False,
        "Germany Marketplace decline": False,
        "UK Enterprise decline": False
    }


    for anomaly in anomalies:

        value = anomaly["value"]
        metric = anomaly["metric"]
        change = anomaly["change"]


        # CASE 1
        if (
            value == "Spain | Laptop Pro"
            and metric == "gross_margin"
            and change < 0
        ):
            tests[
                "Spain Laptop Pro margin deterioration"
            ] = True


        # CASE 2
        if (
            value == "Germany | Marketplace"
            and metric in [
                "orders",
                "revenue",
                "active_customers"
            ]
            and change < 0
        ):
            tests[
                "Germany Marketplace decline"
            ] = True


        # CASE 3
        if (
            value == "United Kingdom | Enterprise"
            and metric in [
                "orders",
                "revenue",
                "active_customers"
            ]
            and change < 0
        ):
            tests[
                "UK Enterprise decline"
            ] = True


    passed = 0

    for name, result in tests.items():

        status = "PASS" if result else "FAIL"

        print(f"{name}: {status}")

        if result:
            passed += 1


    total = len(tests)

    print("\n" + "=" * 60)

    print(
        f"FINAL RESULT: {passed}/{total}"
    )

    print(
        f"Detection rate: "
        f"{passed / total:.0%}"
    )


if __name__ == "__main__":
    run_evaluation()