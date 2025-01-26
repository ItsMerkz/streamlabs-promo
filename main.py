import threading
from colorama import *
import threading, time, sys
from Source.Creator.Creator import *
import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config
from Source.Solver.CustomSolver.Api_Server import *
from threading import local, Lock

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

def run():
    while True:
        try:
            gen = Streamlabs()
            gen.register()
        except Exception as e:
            time.sleep(5)


def start_threads():
    threads = []
    thread_count = config["Setting"]["Threads"]
    for _ in range(thread_count):
        t = threading.Thread(target=run, daemon=True)
        t.start()
        threads.append(t)
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Main program exiting. Threads will terminate.")


async def start_server_and_threads():
    config2 = Config()
    config2.bind = "127.0.0.1:8080"
    config2.loglevel = "critical"

    thread_task = asyncio.create_task(asyncio.to_thread(start_threads))

    if config['Captcha']['Captcha_Type'] == "Custom":
        print(f"{timestamp()} | {Fore.LIGHTBLUE_EX}SOLVER{Fore.RESET}  | Captcha Type is Set As Custom [{Fore.LIGHTBLUE_EX}Solver{Fore.RESET}: Custom]")
        server_task = asyncio.create_task(serve(TurnstileAPIServer().app, config2))

        try:
            await asyncio.gather(thread_task, server_task)
        except KeyboardInterrupt:
            print("Interrupted by user. Stopping server and threads...")
            server_task.cancel()
            await server_task
    else:
        print(f"Captcha_Type is '{config['Captcha']['Captcha_Type']}'. Running threads only.")
        try:
            await thread_task
        except KeyboardInterrupt:
            print("Interrupted by user.")

if __name__ == "__main__":
        asyncio.run(start_server_and_threads())