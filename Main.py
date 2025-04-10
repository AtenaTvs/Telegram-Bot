import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = os.environ.get("ADMIN_IDS").split(',')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! An admin will contact you soon.")

async def forward_to_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for admin_id in ADMIN_IDS:
        await context.bot.send_message(chat_id=admin_id, text=f"Message from {update.message.chat.id}:\n{update.message.text}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admins))

app.run_polling()
