from google import genai
from google.genai import types
from google.genai.client import Client
import os
import json
import re   

import json
from typing import Dict


def _strip_fences(txt: str) -> str:
    txt = txt.strip()
    if txt.startswith("```"):
        nl = txt.find("\n")
        if nl != -1:
            txt = txt[nl + 1 :]
        if txt.endswith("```"):
            txt = txt[:-3]
    return txt.strip()


def _first_json_object_slice(s: str) -> str:
    # O(n) – balanceia chaves ignorando texto dentro de strings
    start = s.find("{")
    if start == -1:
        raise json.JSONDecodeError("no JSON object found", s, 0)

    depth = 0
    in_str = False
    esc = False

    for i in range(start, len(s)):
        ch = s[i]

        if esc:
            esc = False
            continue

        if ch == "\\":
            esc = True
            continue

        if ch == '"':
            in_str = not in_str
            continue

        if in_str:
            continue

        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return s[start : i + 1]

    raise json.JSONDecodeError("unterminated JSON object", s, start)


def _coerce_json(txt: str) -> Dict:
    body = _strip_fences(txt)
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return json.loads(_first_json_object_slice(body))


def teste(texto: str):

    client = Client(api_key=os.getenv("GOOGLE_API_KEY"))
    prompt = f"extraia as informacoes chave e transforme em um json valido: {texto}"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=1024,
            temperature=0.5,
        )
    )
    txt = _coerce_json(response.text)

    return {'response': txt}