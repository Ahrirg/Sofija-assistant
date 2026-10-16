from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse

from ..utils.Logging import log
from ..LLM.LLM import LLM


app = FastAPI()
ai = LLM()

HTML_PATH = Path(__file__).parent / "chat_test.html"


@app.get("/chat_test")
def chat_test():
    return FileResponse(HTML_PATH, media_type="text/html")


@app.get("/history")
def history():
    return ai.get_history()


@app.get("/ask")
def ask(message: str):
    msg = ai.ask(message)
    log(msg)
    return msg


def run(
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    run()