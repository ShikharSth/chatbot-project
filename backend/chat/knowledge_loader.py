import os
import json
import re

# backend/knowledge/
#   detail.json
#   detail.txt
#   pricing.py

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "knowledge")


def search_knowledge(user_text):
    """
    SUPER FAST knowledge search

    Supports:
    - order lookup from detail.json
    - policy/info from detail.txt
    - config/code values from .py files

    Returns only relevant context.
    """

    user_text = (user_text or "").lower().strip()

    results = []

    # =====================================================
    # 1. SEARCH ORDER ID IN JSON
    # =====================================================
    order_match = re.search(r'\b\d{3,10}\b', user_text)

    if order_match:
        order_id = order_match.group()

        json_path = os.path.join(KNOWLEDGE_DIR, "detail.json")

        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if isinstance(data, list):
                    for item in data:
                        if str(item.get("order_id", "")) == order_id:
                            return (
                                "ORDER FOUND:\n"
                                + json.dumps(item, indent=2)
                            )

                elif isinstance(data, dict):
                    if str(data.get("order_id", "")) == order_id:
                        return (
                            "ORDER FOUND:\n"
                            + json.dumps(data, indent=2)
                        )

            except Exception:
                pass

    # =====================================================
    # 2. SEARCH TEXT FILE (policy / faq / company info)
    # =====================================================
    txt_path = os.path.join(KNOWLEDGE_DIR, "detail.txt")

    if os.path.exists(txt_path):
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read()

            # Split by paragraphs
            chunks = text.split("\n\n")

            for chunk in chunks:
                chunk_lower = chunk.lower()

                # keyword match
                if any(word in chunk_lower for word in user_text.split()):
                    results.append(chunk.strip())

        except Exception:
            pass

    # =====================================================
    # 3. SEARCH PY FILES
    # =====================================================
    for file in os.listdir(KNOWLEDGE_DIR):
        if file.endswith(".py"):
            py_path = os.path.join(KNOWLEDGE_DIR, file)

            try:
                with open(py_path, "r", encoding="utf-8") as f:
                    code = f.read()

                lines = code.splitlines()

                for line in lines:
                    line_lower = line.lower()

                    if any(word in line_lower for word in user_text.split()):
                        results.append(line.strip())

            except Exception:
                pass

    # =====================================================
    # 4. RETURN MATCHES
    # =====================================================
    if results:
        return "\n".join(results[:5])[:3000]

    # =====================================================
    # 5. NOTHING FOUND
    # =====================================================
    return "No relevant company knowledge found."






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
