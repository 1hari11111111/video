# ================================================================
#  MONGODB DATABASE MANAGER
# ================================================================

from pymongo import MongoClient
import datetime

# ------------------------------------------------
# CHANGE THIS TO YOUR MONGODB CONNECTION STRING
# ------------------------------------------------
MONGO_URI = "mongodb://localhost:27017"   # <-- Replace if using Atlas
DB_NAME = "telegram_video_system"


client = MongoClient(MONGO_URI)
db = client[DB_NAME]


# ================================================================
# USERS COLLECTION
# ================================================================
def create_user(user_id):
    if db.users.find_one({"user_id": user_id}) is None:
        db.users.insert_one({
            "user_id": user_id,
            "points": 0,
            "referrals": 0,
            "joined": datetime.datetime.utcnow(),
            "banned": False
        })


def get_user(user_id):
    return db.users.find_one({"user_id": user_id})


def add_points(user_id, amount):
    db.users.update_one({"user_id": user_id}, {"$inc": {"points": amount}})


def remove_points(user_id, amount):
    db.users.update_one({"user_id": user_id}, {"$inc": {"points": -amount}})


def ban_user(user_id):
    db.users.update_one({"user_id": user_id}, {"$set": {"banned": True}})


def unban_user(user_id):
    db.users.update_one({"user_id": user_id}, {"$set": {"banned": False}})



# ================================================================
# FORCE SUBSCRIPTION COLLECTION
# ================================================================
def add_force_sub(channel_username):
    db.force_sub.update_one({"channel": channel_username}, {"$set": {"channel": channel_username}}, upsert=True)


def remove_force_sub(channel_username):
    db.force_sub.delete_one({"channel": channel_username})


def get_force_sub_channels():
    return [c["channel"] for c in db.force_sub.find()]



# ================================================================
# CATEGORIES COLLECTION
# ================================================================
def add_category(key, name, description=""):
    db.categories.update_one(
        {"key": key},
        {"$set": {"name": name, "description": description}},
        upsert=True
    )


def delete_category(key):
    db.categories.delete_one({"key": key})


def get_categories():
    return list(db.categories.find())



# ================================================================
# VIDEO CHANNELS COLLECTION (MULTI-CHANNEL)
# ================================================================
def add_video_channel(name, channel_id):
    db.channels.update_one(
        {"name": name},
        {"$set": {"channel_id": channel_id}},
        upsert=True
    )


def remove_video_channel(name):
    db.channels.delete_one({"name": name})


def get_all_video_channels():
    return list(db.channels.find())



# ================================================================
# VIDEOS COLLECTION
# ================================================================
def add_video(title, category, channel_name, file_id, price):
    db.videos.insert_one({
        "title": title,
        "category": category,
        "channel": channel_name,
        "file_id": file_id,
        "price": price,
        "added": datetime.datetime.utcnow()
    })


def get_videos_by_category(category):
    return list(db.videos.find({"category": category}))


def get_video(video_id):
    return db.videos.find_one({"_id": video_id})



# ================================================================
# TOKEN SYSTEM (FOR VIDEO BOT)
# ================================================================
def save_token(token, user_id, video_data, expire_minutes=5):
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=expire_minutes)

    db.tokens.insert_one({
        "token": token,
        "user_id": user_id,
        "video": video_data,
        "expires": expiry,
        "used": False
    })


def verify_token(token):
    data = db.tokens.find_one({"token": token})

    if not data:
        return None
    
    if data["used"]:
        return None

    if datetime.datetime.utcnow() > data["expires"]:
        return None

    # Mark token as used
    db.tokens.update_one({"token": token}, {"$set": {"used": True}})

    return data["video"]



# ================================================================
# SETTINGS COLLECTION (GLOBAL CONFIG)
# ================================================================
def get_setting(key, default=None):
    row = db.settings.find_one({"key": key})
    return row["value"] if row else default


def set_setting(key, value):
    db.settings.update_one({"key": key}, {"$set": {"value": value}}, upsert=True)
