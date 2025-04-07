from scrapers.google_maps_scraper import search_google_maps
from scrapers.linkedin_scraper import search_linkedin
from scrapers.instagram_scraper import search_instagram
from sheets import salvar_leads
from telegram import Bot
from config import TELEGRAM_TOKEN

bot = Bot(token=TELEGRAM_TOKEN)

async def leadhunter_handler(chat_id, termos_busca):
    try:
        await bot.send_message(chat_id=chat_id, text="🚀 Iniciando busca de leads!")

        leads = []

        # Google Maps
        google_leads = search_google_maps(termos_busca)
        leads.extend(google_leads)
        await bot.send_message(chat_id=chat_id, text=f"🗺️ Google Maps: {len(google_leads)} leads encontrados.")

        # LinkedIn
        linkedin_leads = search_linkedin(termos_busca)
        leads.extend(linkedin_leads)
        await bot.send_message(chat_id=chat_id, text=f"💼 LinkedIn: {len(linkedin_leads)} leads encontrados.")

        # Instagram
        instagram_leads = search_instagram(termos_busca)
        leads.extend(instagram_leads)
        await bot.send_message(chat_id=chat_id, text=f"📸 Instagram: {len(instagram_leads)} leads encontrados.")

        if leads:
            salvar_leads(leads)
            await bot.send_message(chat_id=chat_id, text="✅ Leads salvos na planilha com sucesso!")
        else:
            await bot.send_message(chat_id=chat_id, text="⚠️ Nenhum lead encontrado nas buscas.")

    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"❌ Erro na prospecção: {str(e)}")
