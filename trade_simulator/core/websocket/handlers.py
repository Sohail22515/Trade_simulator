# core/websocket/handler.py

def handle_orderbook_message(message):
    if message.get("type") == "snapshot":
        return "snapshot", message["data"]
    elif message.get("type") == "update":
        return "update", message["data"]
    return "unknown", message
