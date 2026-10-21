import time
from datetime import datetime

#helper functions
def days_to_sec(days: int):
    return days * 24 * 60 * 60 

def convert_time_dif_to_sec(days: int, hours: int, minutes: int) -> int:
    sec_time = hours * 60 * 60
    sec_time += minutes * 60
    sec_time += days_to_sec(days)

    return sec_time


#sofija functions

def sleep_for_time(days: int, hours: int, minutes: int, seconds: int):
    sec = convert_time_dif_to_sec(days, hours, minutes) + seconds
    time.sleep(sec)

def get_current_time() -> str:
    return datetime.today().strftime('%Y-%m-%d %H:$M')


def get_tool_usage_prompt() -> str:
    return "".join(
        'Tool for managing time\n'
        "'tool:sleep_for_time(days: int, hours: int, minutes: int, seconds: int)' can be used to make agent sleep for specified time, 1 minute, 10 minutes or 1 day. Example usage 'tool:sleep_for_time(0,0,10,5)'"
        "'tool:get_current_time()' can be used to get current date and time. Example usage 'tool:get_current_time()'\n"
    )

def get_tools() -> list[dict]:
    return [
        {"command": "sleep_for_time", "args": ["int", "int", "int", "int"], "func": sleep_for_time},
        {"command": "get_current_time", "args": [], "func": get_current_time}
    ]