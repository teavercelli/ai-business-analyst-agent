from agent.agent import ask_agent


TEST_CASES = [
    {
        "name": "Spain margin root cause",

        "prompt": """
        Investiga il deterioramento del gross margin in Spain
        nel periodo luglio-settembre 2026.
        Identifica la root cause usando il database.
        """,

        "checks": {
            "country": ["spain", "spagna"],
            "product": ["laptop pro"],
            "old_cost": ["700"],
            "new_cost": ["1015", "1.015"],
            "margin_after": ["7.7", "7,7"]
        }
    }
]


def run_evaluation():

    passed_tests = 0

    print("\nAGENT EVALUATION")
    print("=" * 50)

    for test in TEST_CASES:

        print(f"\nTest: {test['name']}")

        answer = ask_agent(test["prompt"])
        answer_lower = answer.lower()

        results = {}

        for check_name, accepted_values in test["checks"].items():

            found = any(
                value.lower() in answer_lower
                for value in accepted_values
            )

            results[check_name] = found

        print("\nCHECKS")

        for check_name, result in results.items():

            symbol = "PASS" if result else "FAIL"

            print(f"{check_name}: {symbol}")

        test_passed = all(results.values())

        if test_passed:

            print("\nTEST RESULT: PASS")
            passed_tests += 1

        else:

            print("\nTEST RESULT: FAIL")

        print("\nAgent answer:")
        print(answer)

    total = len(TEST_CASES)

    print("\n" + "=" * 50)

    print(
        f"FINAL RESULT: "
        f"{passed_tests}/{total} tests passed"
    )


if __name__ == "__main__":
    run_evaluation()