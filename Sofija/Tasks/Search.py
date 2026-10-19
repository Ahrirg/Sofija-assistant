import requests
from ddgs import DDGS
from dataclasses import dataclass

from ..utils.Logging import log

@dataclass
class Result():
    id: int
    title: str
    url: str
    description: str

class Search():
    def __init__(self):
        self.results: list[Result] = []

    def search(self, query: str) -> list:
        try:
            results = DDGS().text(query, max_results=10)
            for id, item in enumerate(results):
                self.results.append(
                    Result(
                        id,
                        item.get("title", ""),
                        item.get("href", ""),
                        item.get("body", ""),
                    )
                )
                            
            log(f"Search: {query} successfull", "Search Engine")
            return self.results
        except Exception as e:
            self.results = []
            log(f"Search: {query} failed, error: {e}", "Search Engine")
            return []

    def create_prompt(self) -> str:
        string = "id | title | description"
        for value in self.results:
            string += f"\n{value.id}. | {value.title} | {value.description}"
        return string

    def _get_result(self, id: int) -> Result | None:
        for result in self.results:
            if result.id == id:
                return result
        return None
    
    def open_website(self, id: int) -> str:
        if len(self.results) == 0:
            return "Please use tool:search_google() first"

        cur_result = self._get_result(id)
        if cur_result:
            log(f"Trying to open {cur_result}", "Search engine")
            try:
                requests.get(cur_result.url)
            except Exception as E:
                log(f"Error {E} while trying to open {cur_result}", "Search engine")
                return f"There was an error while trying to open a website id={cur_result.id}"

        return f"Website with id {id} was not found"

Search_engine = Search()

def search_google(query: str):
    Search_engine.search(query)
    return Search_engine.create_prompt()

def open_website(ids: list[int]):
    rez = ""
    for id in ids:
        rez += Search_engine.open_website(id)
    return rez


def get_tool_usage_prompt() -> str:
    return "".join(
        'Tool for managing search options. You can search for them and delete\n'
        "'tool:search_google(query: str)' can be used to search google for websites that then could be opened, Then table with id's | titles | descriptions wil be provided. Example usage 'tool:search_google('Github')'"
        "'tool:open_website(id: int)' can be used to open website by their id, CANNOT BE USED BEFORE THE search_google() function. Example usage 'tool:open_website(2)'\n"
    )

def get_tools() -> list[dict]:
    return [
        {"command": "search_google", "args": ["str"], "func": search_google},
        {"command": "open_website", "args": ["int..."], "func": open_website},
    ]
