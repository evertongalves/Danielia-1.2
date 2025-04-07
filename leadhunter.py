from scrapers.google_maps_scraper import search_google_maps
from scrapers.linkedin_scraper import search_linkedin
from scrapers.instagram_scraper import search_instagram
from scrapers.facebook_scraper import search_facebook
from scrapers.google_search_scraper import search_google_search
from scrapers.yelp_scraper import search_yelp
from scrapers.yellow_pages_scraper import search_yellow_pages
from scrapers.foursquare_scraper import search_foursquare
from sheets import salvar_leads
from telegram import Bot
from config import TELEGRAM_TOKEN

bot = Bot(token=TELEGRAM_TOKEN)

async def leadhunter_handler(chat_id, termos_busca):
    try:
        await bot.send_message(chat_id=chat_id, text="🚀 Iniciando busca de leads!")

        leads = []

        scrapers = [
            ("🗺️ Google Maps", search_google_maps),
            ("💼 LinkedIn", search_linkedin),
            ("📸 Instagram", search_instagram),
            ("📘 Facebook", search_facebook),
            ("🔍 Google Search", search_google_search),
            ("🧭 Yelp", search_yelp),
            ("📒 Yellow Pages", search_yellow_pages),
            ("📍 Foursquare", search_foursquare),
        ]

        for name, scraper_func in scrapers:
            scraper_leads = scraper_func(termos_busca)
            leads.extend(scraper_leads)
            await bot.send_message(chat_id=chat_id, text=f"{name}: {len(scraper_leads)} leads encontrados.")

        if leads:
            salvar_leads(leads)
            await bot.send_message(chat_id=chat_id, text="✅ Leads salvos na planilha com sucesso!")
        else:
            await bot.send_message(chat_id=chat_id, text="⚠️ Nenhum lead encontrado nas buscas.")

    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"❌ Erro na prospecção: {str(e)}")
