import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is not set. "
        "Add it to backend/.env"
    )


client = OpenAI(api_key=api_key)


LLM_MODEL = "gpt-4.1-mini"


def generate_answer(
    question: str,
    context: str,
) -> str:
    """
    Generate an answer using the retrieved code context.
    """

    prompt = f"""
You are CodeAtlas, an AI assistant that helps developers
understand software repositories.

Answer the user's question using ONLY the provided code context.

If the context does not contain enough information to answer
the question, clearly say that you could not find enough
information in the indexed code.

Do not invent files, functions, classes, or behavior.

When possible, mention the relevant file names, symbols,
and line numbers from the context.

CODE CONTEXT:
----------------
{context}
----------------

USER QUESTION:
{question}

Provide a clear and concise explanation.
"""

    response = client.responses.create(
        model=LLM_MODEL,
        input=prompt,
    )

    return response.output_text