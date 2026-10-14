import json
import os
import time
from ..utils import env
from enum import Enum
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class api_endpoint(Enum):
    Google = 1
    Llama_cpp = 2

class GoogleEndpoint():
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(self, model: str, api_key: str) -> None:
        self.api_key = api_key
        self.model = model
        self.payload: dict = {
            "contents": []
        }

    def get_models(self) -> list[dict]:
        url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models?key={self.api_key}"
        )

        request = Request(
            url,
            headers={"Content-Type": "application/json"},
            method="GET",
        )

        try:
            with urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))

            list_models = []
            for model in result.get("models", []):
                list_models.append({"name": model.get("name", ""), "desc": model.get("description", "")})

            return list_models

        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Google API HTTP {exc.code}: {error_body}"
            ) from exc

        except URLError as exc:
            raise RuntimeError(
                f"Failed to connect to Google API: {exc.reason}"
            ) from exc

    def add_to_payload(self, role: str, message: str, payload: dict | None) -> None:
        pl = payload if payload != None else self.payload

        pl["contents"].append({
            "role": role,
            "parts": [{"text": message}]
        })

    def ask(self, message: str) -> str:
        url = f"{self.BASE_URL}/{self.model}:generateContent"

        cur_payload = json.loads(json.dumps(self.payload))


        self.add_to_payload("user", message, cur_payload)

        request = Request(
            url,
            data=json.dumps(cur_payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            },
            method="POST",
        )

        max_retries = 5
        backoff_factor = 2
        for attempt in range(max_retries):
            try:
                with urlopen(request, timeout=60) as response:
                    result = json.loads(response.read().decode("utf-8"))

                candidates = result.get("candidates", [])
                if not candidates:
                    raise RuntimeError(
                        f"No response candidates returned: {result}"
                    )

                parts = candidates[0].get("content", {}).get("parts", [])
                result_text = "".join(
                    part["text"]
                    for part in parts
                    if "text" in part
                )

                self.add_to_payload("model", result_text, cur_payload)
                self.payload = cur_payload
                return result_text

            except HTTPError as exc:
                error_body = exc.read().decode("utf-8", errors="replace")
                if exc.code in [429, 500, 502, 503, 504] and attempt < max_retries - 1:
                    time.sleep(backoff_factor ** attempt)
                    continue
                raise RuntimeError(
                    f"Google API HTTP {exc.code}: {error_body}"
                ) from exc

            except URLError as exc:
                if attempt < max_retries - 1:
                    time.sleep(backoff_factor ** attempt)
                    continue
                raise RuntimeError(
                    f"Failed to connect to Google API: {exc.reason}"
                ) from exc

        return ""


class LLM():
    def __init__(self, type: api_endpoint = api_endpoint.Google) -> None:
        self.ApiEndpoint: GoogleEndpoint = GoogleEndpoint(os.environ["GOOGLE_MODEL"], os.environ["GOOGLE_API_KEY"])

    def ask(self, message: str) -> str:
        return self.ApiEndpoint.ask(message)

    def get_history(self) -> dict:
        return json.loads(json.dumps(self.ApiEndpoint.payload))