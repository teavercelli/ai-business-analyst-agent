from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

from agent.tools import query_database, monitor_business
from agent.prompts import SYSTEM_PROMPT


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = "gemini-flash-lite-latest"


def ask_agent(question: str):

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=question)
            ]
        )
    ]

    # Massimo 20 passaggi per evitare loop infiniti
    for _ in range(20):

        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=[
                    query_database,
                    monitor_business
                ],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            )
        )

        model_content = response.candidates[0].content
        contents.append(model_content)

        function_calls = [
            part.function_call
            for part in model_content.parts
            if part.function_call is not None
        ]

        # Se Gemini non chiede tool, abbiamo la risposta finale
        if not function_calls:
            return response.text

        function_response_parts = []

        for function_call in function_calls:

            name = function_call.name
            args = dict(function_call.args)

            print(f"\n[Agent usa tool: {name}]")

            if name == "query_database":
                result = query_database(**args)

            elif name == "monitor_business":
                result = monitor_business()

            else:
                result = {
                    "error": f"Tool sconosciuto: {name}"
                }

            function_response_parts.append(
                types.Part.from_function_response(
                    name=name,
                    response={
                        "result": result
                    }
                )
            )

        contents.append(
            types.Content(
                role="user",
                parts=function_response_parts
            )
        )

    return """
Investigation incomplete.

The agent reached the maximum number of investigation steps
before collecting sufficient evidence for a reliable conclusion.

No root cause should be considered confirmed.
"""