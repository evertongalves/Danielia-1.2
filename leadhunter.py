import asyncio
import os
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
        await bot.send_message(chat_id=chat_id, text="🚀 Iniciando busca de leads! Isso pode levar alguns minutos...")

        leads = []
        spreadsheet_id = os.getenv("GOOGLE_SHEETS_KEY")  # ✅ Pegando o ID da planilha do .env

        async def run_scraper(scraper_func, nome_fonte):
            try:
                # Executa o scraper em thread separada
                fonte_leads = await asyncio.to_thread(scraper_func, termos_busca)
                # Filtra apenas leads com email ou telefone
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

        # Executa todas as tarefas em paralelo
        await asyncio.gather(*tasks)

        if leads:
            salvar_leads(leads, spreadsheet_id)
            await bot.send_message(chat_id=chat_id, text="✅ Leads salvos na planilha com sucesso!")
        else:
            await bot.send_message(chat_id=chat_id, text="⚠️ Nenhum lead encontrado nas buscas.")

    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"❌ Erro inesperado: {str(e)}")
