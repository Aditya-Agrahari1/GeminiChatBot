from datetime import datetime
from .mongodb import Database

class UserModel:
    def __init__(self):
        self.db = Database()

    def update_user(self, user_id: int, name: str):
        return self.db.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "name": name,
                    "last_interaction": datetime.utcnow()
                },
                "$setOnInsert": {
                    "user_id": user_id,
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    def get_user(self, user_id: int):
        return self.db.users.find_one({"user_id": user_id})

class MessageModel:
    def __init__(self):
        self.db = Database()

    def store_message(self, user_id: int, text: str, is_bot: bool):
        new_message = {
            "text": text,
            "role": "bot" if is_bot else "user",
            "timestamp": datetime.utcnow()
        }
        
        return self.db.messages.update_one(
            {"user_id": user_id},
            {
                "$push": {"conversation": new_message},
                "$setOnInsert": {"user_id": user_id}
            },
            upsert=True
        )

    def get_chat_history(self, user_id: int, limit: int = 10) -> str:
        conversation_doc = self.db.messages.find_one({"user_id": user_id})
        if not conversation_doc or not conversation_doc.get('conversation'):
            return ""
        
        messages = conversation_doc['conversation'][-limit:]
        history = []
        for msg in messages:
            role = "Bot" if msg["role"] == "bot" else "User"
            history.append(f"{role}: {msg['text']}")
        
        return "\n".join(history)