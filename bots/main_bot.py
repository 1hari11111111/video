# ================================================================
#  MAIN BOT (BOT A)
#  Handles:
#   • Points System
#   • Referral System
#   • Categories
#   • Video list
#   • Force Subscription
#   • Token Generation
#   • Admin Commands
#   • MongoDB Storage
# ================================================================

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import uuid
import requests

from bots.config import (
    BOT_A_TOKEN,
    VERIFY_TOKEN_URL,
    SAVE_TOKEN_URL,
    REFERRAL_REWARD
)

from bots import database as db
from bots.utils import (
    is_admin,
    generate_token,
    check_force_subscription,
    force_sub_keyboard,
    format_categories_list,
    format_channels_list,
    log
)


bot = telebot.TeleBot(BOT_A_TOKEN, parse_mode="Markdown")


# ================================================================
# START COMMAND (REFERRAL + CREATE USER)
# ================================================================
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    # Create user if not exists
    db.create_user(user_id)

    # Handle referral
    try:
        cmd = message.text.split()
        if len(cmd) > 1:
            ref_id = int(cmd[1])
            if ref_id != user_id:
                ref_user = db.get_user(ref_id)
                if ref_user:
                    db.add_points(ref_id, REFERRAL_REWARD)
                    bot.send_message(ref_id, f"🎉 *You earned {REFERRAL_REWARD} points!*")
    except:
        pass

    # Force subscription check
    sub_status = check_force_subscription(bot, user_id)
    if sub_status is not True:
        ok, not_joined = sub_status
        bot.send_message(
            user_id,
            "❗ *You must join all required channels to use the bot.*",
            reply_markup=force_sub_keyboard()
        )
        return

    main_menu(user_id)


# ================================================================
# MAIN MENU
# ================================================================
def main_menu(chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎬 Videos", "💰 My Points")
    markup.row("ℹ️ Help")

    if is_admin(chat_id):
        markup.row("🛠 Admin Panel")

    bot.send_message(chat_id, "👋 *Welcome to the Video Bot!*", reply_markup=markup)


# ================================================================
# CALLBACK HANDLER FOR FORCE-SUB CHECK
# ================================================================
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def recheck_subscription(call):
    user_id = call.from_user.id
    status = check_force_subscription(bot, user_id)

    if status is True:
        bot.send_message(user_id, "✅ *Thanks! You may continue.*")
        main_menu(user_id)
    else:
        bot.send_message(
            user_id,
            "❗ *You must join all required channels first!*",
            reply_markup=force_sub_keyboard()
        )


# ================================================================
# TEXT MESSAGE HANDLER
# ================================================================
@bot.message_handler(func=lambda m: True)
def menu_router(message):
    text = message.text
    user_id = message.from_user.id

    # Force subscription check always
    sub_status = check_force_subscription(bot, user_id)
    if sub_status is not True:
        bot.send_message(
            user_id,
            "❗ *You must join all required channels first!*",
            reply_markup=force_sub_keyboard()
        )
        return

    if text == "💰 My Points":
        user = db.get_user(user_id)
        bot.send_message(user_id, f"💰 *Your Points:* `{user['points']}`")
        return

    if text == "🎬 Videos":
        show_categories(user_id)
        return

    if text == "ℹ️ Help":
        bot.send_message(
            user_id,
            "📌 *Help Menu*\n\n"
            "• Earn points by inviting others.\n"
            "• Use points to unlock videos.\n"
            "• Videos are delivered from private channels.\n"
            "• Contact admin for issues."
        )
        return

    if text == "🛠 Admin Panel" and is_admin(user_id):
        show_admin_menu(user_id)
        return


# ================================================================
# SHOW CATEGORIES
# ================================================================
def show_categories(chat_id):
    cats = db.get_categories()

    if not cats:
        bot.send_message(chat_id, "⚠️ No categories added yet.")
        return

    markup = InlineKeyboardMarkup()
    for c in cats:
        markup.add(InlineKeyboardButton(c["name"], callback_data=f"cat_{c['key']}"))

    bot.send_message(chat_id, "🎬 *Choose a category:*", reply_markup=markup)


# ================================================================
# CATEGORY → SHOW VIDEOS
# ================================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def show_videos(call):
    user_id = call.from_user.id
    key = call.data.replace("cat_", "")

    videos = db.get_videos_by_category(key)

    if not videos:
        bot.answer_callback_query(call.id, "No videos in this category.")
        return

    markup = InlineKeyboardMarkup()

    for v in videos:
        markup.add(
            InlineKeyboardButton(
                f"{v['title']} — {v['price']} pts",
                callback_data=f"video_{v['_id']}"
            )
        )

    bot.send_message(user_id, f"🎬 *Videos in {key}:*", reply_markup=markup)


# ================================================================
# VIDEO SELECTED → CHECK POINTS & CREATE TOKEN
# ================================================================
from bson import ObjectId

@bot.callback_query_handler(func=lambda call: call.data.startswith("video_"))
def unlock_video(call):
    user_id = call.from_user.id

    video_id = call.data.replace("video_", "")
    video = db.get_video(ObjectId(video_id))

    if not video:
        bot.answer_callback_query(call.id, "Video not found.")
        return

    user = db.get_user(user_id)

    if user["points"] < video["price"]:
        bot.send_message(user_id, "❌ *Not enough points!*")
        return

    # Deduct points
    db.remove_points(user_id, video["price"])

    # Generate token
    token = generate_token()

    # Prepare data to save
    token_payload = {
        "video_id": str(video["_id"]),
        "channel": video["channel"],
        "file_id": video["file_id"],
        "title": video["title"]
    }

    # Save token in MongoDB
    db.save_token(token, user_id, token_payload)

    # Send Bot-2 link
    bot.send_message(
        user_id,
        f"🎬 *Your video is ready!*\n\n"
        "Click below to watch:\n"
        f"https://t.me/YourVideoBot?start={token}\n\n"
        "_Video will auto-delete in 5 minutes._"
    )


# ================================================================
# ADMIN COMMANDS
# ================================================================
def show_admin_menu(chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("➕ Add Category", "❌ Remove Category")
    markup.row("📂 List Categories")
    markup.row("📡 Add Channel", "🚫 Remove Channel")
    markup.row("🔗 ForceSub Add", "🔗 ForceSub Remove")
    markup.row("🎥 Add Video")
    markup.row("⬅️ Back")
    
    bot.send_message(chat_id, "🛠 *Admin Panel:*", reply_markup=markup)



# ================================================================
# ADMIN TEXT ROUTER
# ================================================================
@bot.message_handler(func=lambda m: is_admin(m.from_user.id))
def admin_router(message):
    text = message.text
    chat_id = message.chat.id

    # Go back to menu
    if text == "⬅️ Back":
        main_menu(chat_id)
        return

    # Categories
    if text == "➕ Add Category":
        bot.send_message(chat_id, "Send category in format:\n`key|Name|Description`")
        bot.register_next_step_handler(message, admin_add_category)
        return

    if text == "❌ Remove Category":
        bot.send_message(chat_id, "Send category key to delete:")
        bot.register_next_step_handler(message, admin_delete_category)
        return

    if text == "📂 List Categories":
        bot.send_message(chat_id, format_categories_list())
        return

    # Video Channels
    if text == "📡 Add Channel":
        bot.send_message(chat_id, "Send in format:\n`name|channel_id`")
        bot.register_next_step_handler(message, admin_add_channel)
        return

    if text == "🚫 Remove Channel":
        bot.send_message(chat_id, "Send channel name to remove:")
        bot.register_next_step_handler(message, admin_remove_channel)
        return

    # Force Sub
    if text == "🔗 ForceSub Add":
        bot.send_message(chat_id, "Send channel username like: `@ChannelName`")
        bot.register_next_step_handler(message, admin_forcesub_add)
        return

    if text == "🔗 ForceSub Remove":
        bot.send_message(chat_id, "Send channel username to remove:")
        bot.register_next_step_handler(message, admin_forcesub_remove)
        return


# ================================================================
# ADMIN FUNCTIONS
# ================================================================
def admin_add_category(message):
    try:
        key, name, desc = message.text.split("|")
        db.add_category(key.strip(), name.strip(), desc.strip())
        bot.send_message(message.chat.id, "✅ Category added!")
    except:
        bot.send_message(message.chat.id, "❌ Invalid format.")

def admin_delete_category(message):
    db.delete_category(message.text.strip())
    bot.send_message(message.chat.id, "🗑 Deleted.")

def admin_add_channel(message):
    try:
        name, channel_id = message.text.split("|")
        db.add_video_channel(name.strip(), int(channel_id.strip()))
        bot.send_message(message.chat.id, "📡 Channel added!")
    except:
        bot.send_message(message.chat.id, "❌ Invalid format.")

def admin_remove_channel(message):
    db.remove_video_channel(message.text.strip())
    bot.send_message(message.chat.id, "🗑 Channel removed.")

def admin_forcesub_add(message):
    db.add_force_sub(message.text.strip())
    bot.send_message(message.chat.id, "🔗 Force-sub channel added!")

def admin_forcesub_remove(message):
    db.remove_force_sub(message.text.strip())
    bot.send_message(message.chat.id, "🔗 Force-sub channel removed!")


# ================================================================
# START BOT POLLING
# ================================================================
print("Bot A is running...")
bot.infinity_polling()
