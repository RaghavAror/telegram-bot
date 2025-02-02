from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from config import Config
from datetime import datetime
import numpy as np

app = FastAPI()

client = MongoClient(Config.MONGO_URI, server_api=ServerApi('1'))
db = client.get_database("telegram_bot")
users_collection = db.get_collection('users')
chat_history_collection = db.get_collection('chat_history')
file_metadata_collection = db.get_collection('file_metadata')
search_history_collection = db.get_collection('web_searches')

@app.get("/dashboard")
async def dashboard():
    try:
        print("got")
        # Get basic statistics
        total_users = users_collection.count_documents({})  # Removed await here

        message_stats = list(chat_history_collection.aggregate([  # list() to execute sync
            {"$group": {
                "_id": None,
                "totalMessages": {"$sum": 1},
                "positive": {"$sum": {"$cond": [{"$eq": ["$sentiment", "positive"]}, 1, 0]}},
                "neutral": {"$sum": {"$cond": [{"$eq": ["$sentiment", "neutral"]}, 1, 0]}},
                "negative": {"$sum": {"$cond": [{"$eq": ["$sentiment", "negative"]}, 1, 0]}}
            }}
        ]))

        file_stats = list(file_metadata_collection.aggregate([  # list() to execute sync
            {"$addFields": {
                "extension": {"$arrayElemAt": [{"$split": ["$filename", "."]}, -1]}
            }},
            {"$group": {
                "_id": "$extension",
                "count": {"$sum": 1}
            }}
        ]))

        # Format results
        result = {
            "total_users": total_users,
            "messages": {
                "total": message_stats[0]["totalMessages"] if message_stats else 0,
                "positive": message_stats[0]["positive"] if message_stats else 0,
                "neutral": message_stats[0]["neutral"] if message_stats else 0,
                "negative": message_stats[0]["negative"] if message_stats else 0
            },
            "files": {str(item["_id"]): item["count"] for item in file_stats}
        }

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
