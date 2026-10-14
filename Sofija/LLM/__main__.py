import os
from . import LLM
from ..utils import env
from ..utils.Logging import log

if __name__ == "__main__":
    log(os.environ["GOOGLE_API_KEY"])
    endpoint = LLM.GoogleEndpoint(os.environ["GOOGLE_MODEL"], os.environ["GOOGLE_API_KEY"])
    models = endpoint.get_models()
    for model in models:
        print(f"Name: {model.get("name", "")} \nDescription: {model.get("desc", "")}\n\n")