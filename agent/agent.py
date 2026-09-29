from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

from agent.tools import query_database, monitor_business
from agent.prompts import SYSTEM_PROMPT


# =========================================================
# CONFIGURAZIONE API KEY
# =========================================================

# Carica la chiave dal file .env quando lavoriamo in locale
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

# Se siamo su Streamlit Cloud, prova a leggere
# la chiave dai Secrets di Streamlit
if not api_key:
    try:
        import streamlit as st
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

# Controllo di sicurezza
if not api_key:
    raise ValueError(
        "GEMINI_API_KEY non trovata. "
        "Configura la chiave nel file .env oppure nei Secrets di Streamlit."
    )


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=api_key
)

MODEL = "gemini-flash-lite-latest"


# =========================================================
# AI AGENT
# =========================================================

def ask_agent(question: str):

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=question
                )
            ]
        )
    ]


    # Massimo 5 passaggi per evitare:
    # - loop infiniti
    # - troppe chiamate API
    # - consumo eccessivo della quota gratuita
    for _ in range(5):

        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=[
                    query_database,
                    monitor_business
                ],
                automatic_function_calling=(
                    types.AutomaticFunctionCallingConfig(
                        disable=True
                    )
                )
            )
        )


        # =================================================
        # RISPOSTA DEL MODELLO
        # =================================================

        model_content = response.candidates[0].content

        contents.append(
            model_content
        )


        # =================================================
        # CERCHIAMO EVENTUALI TOOL CALL
        # =================================================

        function_calls = [
            part.function_call
            for part in model_content.parts
            if part.function_call is not None
        ]


        # Se Gemini non richiede altri tool,
        # significa che ha prodotto la risposta finale.
        if not function_calls:
            return response.text


        # =================================================
        # ESECUZIONE DEI TOOL
        # =================================================

        function_response_parts = []

        for function_call in function_calls:

            name = function_call.name
            args = dict(
                function_call.args
            )

            print(
                f"\n[Agent usa tool: {name}]"
            )


            # ---------------------------------------------
            # SQL TOOL
            # ---------------------------------------------

            if name == "query_database":

                result = query_database(
                    **args
                )


            # ---------------------------------------------
            # BUSINESS MONITOR
            # ---------------------------------------------

            elif name == "monitor_business":

                result = monitor_business()


            # ---------------------------------------------
            # TOOL SCONOSCIUTO
            # ---------------------------------------------

            else:

                result = {
                    "error": (
                        f"Tool sconosciuto: {name}"
                    )
                }


            # Restituiamo il risultato del tool
            # al modello
            function_response_parts.append(
                types.Part.from_function_response(
                    name=name,
                    response={
                        "result": result
                    }
                )
            )


        # =================================================
        # RISULTATI DEI TOOL → GEMINI
        # =================================================

        contents.append(
            types.Content(
                role="user",
                parts=function_response_parts
            )
        )


    # =====================================================
    # LIMITE MASSIMO RAGGIUNTO
    # =====================================================

    return """
Investigation incomplete.

The agent reached the maximum number of investigation steps
before collecting sufficient evidence for a reliable conclusion.

No root cause should be considered confirmed.
"""