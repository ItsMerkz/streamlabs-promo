from threading import Lock
import threading
from urllib.parse import unquote
lock = Lock()

def remove_content(filename, delete_line: str) -> None:
    with lock:
        with open(filename, "r+") as io:
            content = io.readlines()
            io.seek(0)
            for line in content:
                if not (delete_line in line):
                    io.write(line)
            io.truncate()
            

