from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_TOKEN, BOT_NAME
from commands import start, help_command, report_command, leadhunter_command
import scheduler

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Desculpe, não entendi o comando. Digite /ajuda para ver o que posso fazer!")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ajuda", help_command))
app.add_handler(CommandHandler("relatorio", report_command))
app.add_handler(CommandHandler("leads", leadhunter_command))  # <-- Handler que você queria
app.add_handler(MessageHandler(filters.COMMAND, unknown))

scheduler.run_scheduler()

app.run_polling()
