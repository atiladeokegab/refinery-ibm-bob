from __future__ import annotations
import os
import requests
from bob.providers import BaseProvider


class IBMBobProvider(BaseProvider):
    def __init__(self) -> None:
        self._api_key = os.environ["WATSONX_API_KEY"]
        self._project_id = os.environ["WATSONX_PROJECT_ID"]
        self._url = os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        self._model = os.environ.get("WATSONX_MODEL", "ibm/granite-13b-chat-v2")

    def complete(self, prompt: str) -> str:
        token = self._get_token()
        resp = requests.post(
            f"{self._url}/ml/v1/text/generation?version=2023-05-29",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "model_id": self._model,
                "input": prompt,
                "parameters": {"decoding_method": "greedy", "max_new_tokens": 600},
                "project_id": self._project_id,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["results"][0]["generated_text"]

    def _get_token(self) -> str:
        resp = requests.post(
            "https://iam.cloud.ibm.com/identity/token",
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self._api_key,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]
