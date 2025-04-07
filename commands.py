from telegram import Update
from telegram.ext import ContextTypes
from config import BOT_NAME

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Olá! Eu sou {BOT_NAME}, seu assistente pessoal. 🚀")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""Posso te ajudar com várias tarefas:

- 📊 /relatorio: Gerar relatório atualizado
- 🤖 Prospecção automatizada
- 💬 Respostas automáticas
- 🔄 Atualização diária
- ✅ Checklist automático
Digite o comando desejado para começar!""")

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Aqui está seu relatório atualizado! 📊")
