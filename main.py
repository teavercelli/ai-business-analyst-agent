from agent.agent import ask_agent
from agent.monitor import run_monitor


print("""
AI BUSINESS ANALYST
-------------------

1 - Chat with Analyst
2 - Run Automatic Business Monitor
3 - Exit
""")


choice = input("Scegli modalità: ")


if choice == "1":

    print("\nModalità Analyst Chat")

    while True:

        question = input("\nTu: ")

        if question.lower() == "exit":
            break

        answer = ask_agent(question)

        print("\nAgent:")
        print(answer)


elif choice == "2":

    print("\nAvvio monitoraggio automatico...\n")

    run_monitor()


elif choice == "3":

    print("Programma terminato.")


else:

    print("Scelta non valida.")