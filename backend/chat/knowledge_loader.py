import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")


def load_all_knowledge():
    data = ""

    for file in os.listdir(KNOWLEDGE_DIR):
        path = os.path.join(KNOWLEDGE_DIR, file)

        if file.endswith(".txt"):
            with open(path, "r", encoding="utf-8") as f:
                data += f.read() + "\n"

        elif file.endswith(".json"):
            with open(path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                data += json.dumps(json_data, indent=2) + "\n"

        elif file.endswith(".py"):
            with open(path, "r", encoding="utf-8") as f:
                data += f.read() + "\n"

    return data
