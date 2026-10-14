from datetime import datetime
from enum import IntEnum

class Level(IntEnum):
    Max = 3
    Min = 2
    Disabled = 1


class Logging():
    def __init__(self, verbose_level: Level = Level.Max, log_file_location: str | None = None) -> None:
        self.file_location  = log_file_location
        self.verbose_level = verbose_level


    def log(self, message: str, sector: str | None = None, level: Level = Level.Max) -> None:
        if level > self.verbose_level:
            return
        
        cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sector_text = sector if sector is not None else ""
        log_message = f"[{cur_time} | {sector_text}] {message}"

        if self.file_location:
            with open(self.file_location, "+a") as f:
                f.write(log_message)

        print(message)


def log(message: str | dict | list, sector: str | None = None, level: Level = Level.Max):
    logObj = Logging()
    logObj.log(str(message), sector, level)