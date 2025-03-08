from pymongo import MongoClient
from config import MONGODB_URI

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.client = MongoClient(MONGODB_URI)
            cls._instance.db = cls._instance.client['telegram_bot']
            # Test connection
            cls._instance.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        return cls._instance

    @property
    def messages(self):
        return self.db.messages

    @property
    def users(self):
        return self.db.users