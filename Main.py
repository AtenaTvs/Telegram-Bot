import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# توکن ربات تلگرام خود را وارد کنید
TOKEN = "your-telegram-bot-token"

# آیدی‌های ادمین
ADMIN_IDS = [7968070502]  # آیدی ادمین‌ها را وارد کنید

# تنظیمات لاگ برای نمایش خطاها
logging.basicConfig(level=logging.INFO)

# دستورات ربات
def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام! من ربات تلگرام شما هستم.")

def help(update: Update, context: CallbackContext):
    update.message.reply_text("کمک می‌خواهید؟")

def main():
    # ایجاد آپداتر و دیسپچر
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # افزودن دستورات به ربات
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # شروع ربات
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
