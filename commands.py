from telegram import Update
from telegram.ext import ContextTypes
from config import BOT_NAME
from leadhunter import leadhunter_handler

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Olá! Eu sou {BOT_NAME}, seu assistente pessoal de prospecção. 🚀")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
Posso te ajudar com várias tarefas:

- 📊 /relatorio: Gerar relatório atualizado
- 🤖 /leadhunter [termo]: Prospecção automatizada
- 💬 Respostas automáticas
- 🔄 Atualização manual
- ✅ Checklist automático

Digite o comando desejado para começar!
""")

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Aqui está seu relatório atualizado! 📊")

async def leadhunter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        termos_busca = " ".join(context.args)
        await leadhunter_handler(update.effective_chat.id, termos_busca)
    else:
        await update.message.reply_text("Por favor, informe o termo para buscar leads. Exemplo: /leadhunter marketing digital São Paulo")
