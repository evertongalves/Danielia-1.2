import asyncio
from telegram import Bot
from config import TELEGRAM_TOKEN
from sheets import salvar_leads
from scrapers import (
    search_google_maps,
    search_linkedin,
    search_instagram,
    search_facebook,
    search_google_search,
    search_yelp,
    search_yellow_pages,
    search_foursquare
)

bot = Bot(token=TELEGRAM_TOKEN)

async def leadhunter_handler(chat_id, termos_busca):
    try:
        await bot.send_message(chat_id=chat_id, text="🚀 Iniciando busca de leads! Isso pode levar alguns minutos...")

        leads = []
        fonte_resultados = {}

        async def run_scraper(scraper_func, nome_fonte):
            try:
                fonte_leads = await asyncio.to_thread(scraper_func, termos_busca)
                fonte_leads = [lead for lead in fonte_leads if lead.get('email') or lead.get('telefone')]

                if fonte_leads:
                    leads.extend(fonte_leads)
                    fonte_resultados[nome_fonte] = len(fonte_leads)
                    await bot.send_message(chat_id=chat_id, text=f"🔍 {nome_fonte}: {len(fonte_leads)} leads encontrados.")
                else:
                    fonte_resultados[nome_fonte] = 0  # Salva no ranking, mas não envia mensagem duplicada
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
            await bot.send_message(chat_id=chat_id, text=f"✅ Leads salvos na planilha com sucesso!")

            # Cria o ranking das fontes
            ranking = sorted(fonte_resultados.items(), key=lambda x: x[1], reverse=True)
            ranking_text = "\n".join([f"{idx+1}️⃣ {fonte}: {qtd} leads" for idx, (fonte, qtd) in enumerate(ranking) if qtd > 0])

            await bot.send_message(chat_id=chat_id, text=f"📊 Busca finalizada! Foram encontrados {total_leads} leads no total.\n\n🏆 Ranking de fontes:\n{ranking_text}")

        else:
            await bot.send_message(chat_id=chat_id, text="⚠️ Nenhum lead encontrado.")

    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"❌ Erro durante a busca de leads: {str(e)}")
