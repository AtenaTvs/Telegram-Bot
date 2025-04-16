import logging
import json
import os
import time
from threading import Thread
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler


# توکن ربات
TOKEN = os.environ.get("TOKEN")

# آیدی عددی ادمین‌ها
admin_ids_str = os.environ.get("ADMIN_IDS", "[]")
ADMIN_IDS = json.loads(admin_ids_str)  

# تبلیغ آخر
last_ad = None
advertisement_interval_seconds = 43200

# چت‌های هدف
target_channels = []

# لاگ برای خطاها
logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_FILE = os.path.join(BASE_DIR, "target_channels.json")


def load_target_channels():
    if os.path.exists(TARGET_FILE):
        with open(TARGET_FILE, "r") as f:
            return json.load(f)  # Returns a list of chat_ids
    return []

# Save target chats to JSON file
def save_target_channels():
    with open(TARGET_FILE, "w") as f:
        json.dump(target_channels, f, indent=4)  # Writes the list to file with nice formatting

def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("نیاز به مشاوره دارم برای امور مهاجرتی", callback_data='consult')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("سلام! به ربات مشاوره مهاجرتی خوش آمدید. برای مهاجرت نیاز به مشاوره دارید؟", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == 'consult':
        user = query.from_user

        if user.username:
            user_display = f"@{user.username}"
        else:
            user_display = f"{user.full_name} (ID: {user.id})"
        message = f"درخواست مشاوره از {user_display}"
        for admin_id in ADMIN_IDS:
            context.bot.send_message(chat_id=admin_id, text=message)
        query.edit_message_text(text="درخواست شما ارسال شد. منتظر پاسخ ادمین باشید.")

def handle_admin_message(update: Update, context: CallbackContext):
    global last_ad , advertisement_interval_seconds
    user_id = update.message.from_user.id
    if user_id in ADMIN_IDS:
        last_ad = update.message
        update.message.reply_text(f"تبلیغ دریافت شد و هر {int(advertisement_interval_seconds // 3600)} ساعت ارسال می‌شود.")
    else:
        update.message.reply_text("شما دسترسی لازم را ندارید.")

def send_advertisement(context: CallbackContext):
    global last_ad
    if last_ad:
        channels = load_target_channels()
        for channel_id in channels:
            try:
                if last_ad.text:
                    context.bot.send_message(chat_id=channel_id, text=last_ad.text)
                elif last_ad.photo:
                    context.bot.send_photo(chat_id=channel_id, photo=last_ad.photo[-1].file_id, caption=last_ad.caption)
                elif last_ad.document:
                    context.bot.send_document(chat_id=channel_id, document=last_ad.document.file_id, caption=last_ad.caption)
            except Exception as e:
                print(f"خطا در ارسال تبلیغ به {channel_id}: {e}")

def register_channel(update: Update, context: CallbackContext):
    chat = update.effective_chat

    if chat.type == "channel":
        save_target_channels(chat.id)
        context.bot.send_message(chat_id=chat.id, text="✅ Channel registered for advertisements.")
    else:
        update.message.reply_text("⛔ This command only works in a channel.")

def schedule_ad_periodically(job_queue):
    job_queue.run_repeating(send_advertisement, interval=int(advertisement_interval_seconds), first=0)  # هر ۱۲ ساعت

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text | Filters.photo | Filters.document, handle_admin_message))
    dp.add_handler(CommandHandler("registerchannel", register_channel))

    schedule_ad_periodically(updater.job_queue)

    updater.start_polling()
    updater.idle()



if __name__ == '__main__':
    main()
