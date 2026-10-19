from ddgs import DDGS

from ..utils.Logging import log


def google_search(query: str, max_results: int = 5) -> list[dict]:
    """Search the web and return structured results."""
    try:
        results = DDGS().text(query, max_results=max_results)
        return [
            {
                "title": item.get("title", ""),
                "url": item.get("href", ""),
                "description": item.get("body", ""),
            }
            for item in results
        ]
    except Exception as e:
        print(f"Search error: {e}")
        return []

class Search():
    def __init__(self):
        self.results = []

    def search_engine(self, query: str) -> list:
        try:
            results = DDGS().text(query, max_results=max_results)
            self.results = [
                {
                    "title": item.get("title", ""),
                    "url": item.get("href", ""),
                    "description": item.get("body", ""),
                }
                for item in results
            ] 
            log(f"Search: {query} successfull", "Search Engine")
            return self.results
        except Exception as e:
            self.results = []
            log(f"Search: {query} failed, error: {e}", "Search Engine")
            return []

    def create_prompt(self) -> str:
        string = "id | title | description"
        for i, value in enumerate(self.results):
            string += f"\n{i}. | {value.title} | {value.description}"
        return string

    def open_website(self, id: int) -> str:
        return "" # TODO


def search_google(query: str):
    pass

def open_website(id: str):
    pass

