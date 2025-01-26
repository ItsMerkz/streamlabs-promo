import json


def load_tasks():
    with open('tasks.json', 'r') as f:
        return json.load(f)

API_KEYS_FILE = 'Data/Output/Api_Keys/api_keys.json'
TASKS_FILE = 'Data/Output/Tasks/tasks.json'
TASKS = {}  # Store tasks with task_id as key

def read_api_keys():
    try:
        with open(API_KEYS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def write_api_keys(api_keys):
    with open(API_KEYS_FILE, 'w') as f:
        json.dump(api_keys, f, indent=4)

def load_tasks_from_file():
    try:
        with open(TASKS_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_tasks_to_file():
    with open(TASKS_FILE, 'w') as file:
        json.dump(TASKS, file, indent=4)

API_KEYS = read_api_keys()
TASKS = load_tasks_from_file()  # Load tasks from file on startup
