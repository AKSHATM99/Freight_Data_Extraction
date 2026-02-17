from pathlib import Path
import json
import asyncio
from prompts import prompt_v1, prompt_v2, prompt_v3
from decouple import config
from langchain_groq import ChatGroq
from schemas import OutputSchema

GROQ_API_KEY = config('GROQ_API_KEY', default=None)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    timeout=None,
    max_retries=3,
    api_key=GROQ_API_KEY,
)

structured_llm = llm.with_structured_output(OutputSchema, method='json_mode')

port_codes_file_path = Path(__file__).parent / "files" / "port_codes.json"
with port_codes_file_path.open() as f:
    port_codes = json.load(f)

input_email_file_path = Path(__file__).parent / "files" / "emails_input.json"
with input_email_file_path.open() as f:
    emails_input = json.load(f)

port_lookup = {
    p["name"].lower(): p["code"]
    for p in port_codes
}

def write_to_file(json_response):
    path = Path("output.json")
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []
    data.append(json_response)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


async def invoke_llm(email):
    chain = prompt_v3 | structured_llm

    response = await chain.ainvoke({
        "port_codes": json.dumps(port_codes, indent=2),
        "email": json.dumps(email, indent=2),
    })

    write_to_file(response.model_dump())

async def main():
    for email in emails_input:
        await invoke_llm(email)
        await asyncio.sleep(3)

asyncio.run(main())
