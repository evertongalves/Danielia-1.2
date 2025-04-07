from telegram import Update
from telegram.ext import ContextTypes
from config import BOT_NAME
from sheets import gerar_relatorio, iniciar_prospeccao

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Olá! Eu sou {BOT_NAME}, seu assistente pessoal. 🚀\n"
        "Pronto para te ajudar com prospecção, relatórios e organização diária!"
    )

# Comando /ajuda
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"""🔧 Aqui está o que posso fazer por você:

- 📊 /relatorio: Gerar relatório atualizado
- 🔎 /prospeccao: Iniciar prospecção automatizada
- 🧩 Fluxo de conversa inteligente: Me pergunte sobre minhas funções!
- 🔄 Atualização diária automática (já ativada)
- ✅ Checklist automático de tarefas concluídas

Pergunte sobre minhas funções para saber mais! 😉"""
    )

# Comando /relatorio
async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Gerando seu relatório atualizado, aguarde um instante...")
    resposta = gerar_relatorio()
    await update.message.reply_text(resposta)

# Comando /prospeccao
async def prospection_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Iniciando a prospecção automatizada...")
    resposta = iniciar_prospeccao()
    await update.message.reply_text(resposta)

# Comando personalizado /sobre
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"""🤖 Eu sou o {BOT_NAME}!

Minhas funções:
• Prospecção automatizada de contatos
• Enriquecimento de dados
• Atualização contínua do Google Sheets
• Geração de relatórios automáticos e organizados
• Conversa natural para responder suas dúvidas!

💡 Tudo isso funcionando de forma automática para você!"""
    )
