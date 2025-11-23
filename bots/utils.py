# ================================================================
#  UTILITY FUNCTIONS FOR BOTH BOTS
# ================================================================

import random
import string
import time
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from bots.config import ADMINS
from bots import database as db


# ================================================================
# RANDOM TOKEN GENERATOR
# ================================================================
def generate_token(length=24):
    """Generate secure random token"""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


# ================================================================
# ADMIN CHECK
# ================================================================
def is_admin(user_id):
    return user_id in ADMINS


# ================================================================
# FORCE SUBSCRIPTION CHECKER
# ================================================================
def check_force_subscription(bot: TeleBot, user_id):
    """
    Returns:
    - True if user joined all required channels
    - (False, list_of_channels_not_joined)
    """
    required = db.get_force_sub_channels()
    
    if not required:
        return True  # No forced channels added yet

    not_joined = []

    for channel in required:
        try:
            status = bot.get_chat_member(channel, user_id)
            if status.status not in ["member", "administrator", "creator"]:
                not_joined.append(channel)
        except:
            not_joined.append(channel)

    return (len(not_joined) == 0, not_joined)


def force_sub_keyboard():
    """Keyboard shown when user has not joined required channels."""
    channels = db.get_force_sub_channels()
    markup = InlineKeyboardMarkup()
    for c in channels:
        markup.add(InlineKeyboardButton(f"Join {c}", url=f"https://t.me/{c.replace('@','')}"))
    markup.add(InlineKeyboardButton("✔️ I Joined", callback_data="check_sub"))
    return markup


# ================================================================
# CATEGORY FORMATTER
# ================================================================
def format_categories_list():
    cats = db.get_categories()
    if not cats:
        return "No categories added yet."

    text = "🎬 *Available Categories:*\n\n"
    for c in cats:
        text += f"• `{c['key']}` — *{c['name']}*\n"
    return text


# ================================================================
# CHANNELS FORMATTER
# ================================================================
def format_channels_list():
    chans = db.get_all_video_channels()
    if not chans:
        return "No video channels added yet."

    text = "📡 *Video Channels Registered:*\n\n"
    for c in chans:
        text += f"• {c['name']} — `{c['channel_id']}`\n"
    return text


# ================================================================
# SAFE DELETE (Bot 2 auto-delete system)
# ================================================================
def safe_delete(bot: TeleBot, chat_id, message_id, delay=300):
    """
    Auto-delete a message after X seconds.
    Used for Bot-2 (video deletion after 5 minutes)
    """
    try:
        time.sleep(delay)
        bot.delete_message(chat_id, message_id)
    except:
        pass


# ================================================================
# LOGGING
# ================================================================
def log(message):
    timestamp = datetime.utcnow().strftime("[%Y-%m-%d %H:%M:%S]")
    try:
        with open("bot_logs.txt", "a") as f:
            f.write(f"{timestamp} {message}\n")
    except:
        pass
