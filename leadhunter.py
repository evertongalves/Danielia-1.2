import asyncio
from telegram import Bot
from sheets import salvar_leads
from scrapers import (
    search_google_maps,
    search_linkedin,
    search_instagram,
    search_facebook,
    search_google_search,
    search_yelp,
    search_yellow_pages,
    search_foursquare,
)
from config import TELEGRAM_TOKEN

bot = Bot(token=TELEGRAM_TOKEN)

async def leadhunter_handler(chat_id, termos_busca):
    try:
        await bot.send_message(chat_id=chat_id, text="🚀 Iniciando busca de leads! Isso pode levar alguns minutos...")

        leads = []

        async def run_scraper(scraper_func, nome_fonte):
            try:
                fonte_leads = await asyncio.to_thread(scraper_func, termos_busca)
                # Filtra leads que tenham email ou telefone
                fonte_leads = [lead for lead in fonte_leads if lead.get('email') or lead.get('telefone')]
                leads.extend(fonte_leads)
                await bot.send_message(chat_id=chat_id, text=f"🔍 {nome_fonte}: {len(fonte_leads)} leads encontrados.")
            except Exception as e:
                await bot.send_message(chat_id=chat_id, text=f"⚠️ Erro na busca {nome_fonte}: {str(e)}")

        tasks = [
            run_scraper(search_google_maps, "Google Maps"),
            run_scraper(search_linkedin, "LinkedIn"),
            run_scraper(search_instagram, "Instagram"),
            run_scraper(search_facebook, "Facebook"),
            run_scraper(search_google_search, "Google Search"),
            run_scraper(search_yelp, "Yelp"),
            run_scraper(search_yellow_pages, "Yellow Pages"),
            run_scraper(search_foursquare, "Foursquare"),
        ]

        await asyncio.gather(*tasks)

        total_leads = len(leads)

        if total_leads:
            salvar_leads(leads)
            await bot.send_message(chat_id=chat_id, text="✅ Leads salvos na planilha com sucesso!")
            await bot.send_message(chat_id=chat_id, text=f"📊 Busca finalizada! Foram encontrados {total_leads} leads no total.")
        else:
            await bot.send_message(chat_id=chat_id, text="⚠️ Nenhum lead encontrado.")

    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"❌ Erro durante a busca de leads: {str(e)}")
