# ================================================================
#  VIDEO BOT (BOT B)
#  Handles:
#    • Token verification
#    • Multi-channel video sending
#    • Auto-delete videos after 5 minutes
#    • MongoDB integration
#    • Admin commands
# ================================================================

import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bots.config import BOT_B_TOKEN, TOKEN_EXPIRY_MINUTES, VIDEO_DELETE_SECONDS
from bots import database as db
from bots.utils import safe_delete, is_admin, log

bot = telebot.TeleBot(BOT_B_TOKEN, parse_mode="Markdown")


# ================================================================
# START COMMAND (TOKEN PROCESSING)
# ================================================================
@bot.message_handler(commands=["start"])
def start(message):
    parts = message.text.split()

    if len(parts) == 1:
        bot.send_message(
            message.chat.id,
            "🎬 Send your unlock link from the main bot to get the video."
        )
        return

    token = parts[1].strip()

    # Verify token via MongoDB
    video_data = db.verify_token(token)

    if not video_data:
        bot.send_message(message.chat.id, "❌ Invalid or expired link.")
        return

    channel = video_data["channel"]
    file_id = video_data["file_id"]
    title = video_data["title"]

    # Send video
    msg = bot.send_message(message.chat.id, f"🎬 *Loading video:* {title} ...")
    
    try:
        sent = bot.send_video(message.chat.id, file_id)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
        return

    # Auto-delete thread
    t = threading.Thread(
        target=safe_delete,
        args=(bot, message.chat.id, sent.message_id, VIDEO_DELETE_SECONDS)
    )
    t.start()

    # Delete info message immediately after video loads
    try:
        bot.delete_message(message.chat.id, msg.message_id)
    except:
        pass


# ================================================================
# ADMIN COMMANDS
# ================================================================
@bot.message_handler(commands=["admin"])
def admin_menu(message):
    if not is_admin(message.from_user.id):
        return

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📡 Channels", callback_data="admin_channels"))
    markup.add(InlineKeyboardButton("🎥 Videos", callback_data="admin_videos"))
    markup.add(InlineKeyboardButton("🔄 Reload", callback_data="admin_reload"))

    bot.send_message(message.chat.id, "🛠 *Video Bot Admin Panel:*", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_actions(call):
    user_id = call.from_user.id
    if not is_admin(user_id):
        return

    if call.data == "admin_reload":
        bot.answer_callback_query(call.id, "Reloaded successfully!")
        return

    if call.data == "admin_channels":
        chans = db.get_all_video_channels()
        if not chans:
            bot.send_message(user_id, "📡 *No video channels registered.*")
            return

        text = "📡 *Registered Video Channels:*\n\n"
        for c in chans:
            text += f"• {c['name']} — `{c['channel_id']}`\n"

        bot.send_message(user_id, text)
        return

    if call.data == "admin_videos":
        vids = list(db.videos.find().limit(20))
        if not vids:
            bot.send_message(user_id, "🎥 No videos stored.")
            return

        text = "🎥 *Recently Added Videos:*\n\n"
        for v in vids:
            text += f"• {v['title']} — Cat: {v['category']} — Channel: {v['channel']}\n"

        bot.send_message(user_id, text)
        return


# ================================================================
# VIDEO BOT IS LIVE
# ================================================================
print("Bot B (Video Delivery Bot) is running...")
bot.infinity_polling()
