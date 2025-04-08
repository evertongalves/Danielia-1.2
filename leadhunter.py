import asyncio
from datetime import datetime
from telegram import Bot
from config import TELEGRAM_TOKEN
from sheets import salvar_leads, carregar_leads_existentes
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

def limpar_duplicados(leads_novos, leads_existentes):
    contatos_existentes = set()

    for lead in leads_existentes:
        if lead.get('email'):
            contatos_existentes.add(lead['email'].lower())
        if lead.get('telefone'):
            contatos_existentes.add(lead['telefone'])

    leads_filtrados = []
    for lead in leads_novos:
        email = lead.get('email', '').lower()
        telefone = lead.get('telefone')
        if (email and email in contatos_existentes) or (telefone and telefone in contatos_existentes):
            continue  # Duplicado, pula!
        leads_filtrados.append(lead)

    return leads_filtrados

async def leadhunter_handler(chat_id, termos_busca):
    try:
        await bot.send_message(chat_id=chat_id, text="🚀 Iniciando busca de leads! Isso pode levar alguns minutos...")

        leads_encontrados = []
        ranking_fontes = {}

        async def run_scraper(scraper_func, nome_fonte):
            try:
                fonte_leads = await asyncio.to_thread(scraper_func, termos_busca)
                # Filtra leads que tenham pelo menos email ou telefone
                fonte_leads = [lead for lead in fonte_leads if lead.get('email') or lead.get('telefone')]

                if fonte_leads:
                    # Marca a fonte para ranking
                    ranking_fontes[nome_fonte] = len(fonte_leads)

                    # Adiciona data e fonte aos leads
                    data_hoje = datetime.now().strftime("%Y-%m-%d")
                    for lead in fonte_leads:
                        lead['data'] = data_hoje
                        lead['fonte'] = nome_fonte

                    leads_encontrados.extend(fonte_leads)
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

        total_leads = len(leads_encontrados)

        if total_leads:
            # Carrega existentes para evitar duplicados
            leads_existentes = carregar_leads_existentes()

            # Limpeza de duplicados
            leads_filtrados = limpar_duplicados(leads_encontrados, leads_existentes)

            if leads_filtrados:
                salvar_leads(leads_filtrados)
                await bot.send_message(chat_id=chat_id, text=f"✅ {len(leads_filtrados)} novos leads salvos na planilha com sucesso!")
            else:
                await bot.send_message(chat_id=chat_id, text="ℹ️ Nenhum novo lead para adicionar. Todos já estavam na planilha.")

            # Envia ranking das melhores fontes
            if ranking_fontes:
                ranking_texto = "\n".join([f"{fonte}: {quantidade}" for fonte, quantidade in sorted(ranking_fontes.items(), key=lambda item: item[1], reverse=True)])
                await bot.send_message(chat_id=chat_id, text=f"📊 Ranking das fontes:\n{ranking_texto}")

            await bot.send_message(chat_id=chat_id, text=f"🎉 Busca finalizada! Total encontrado hoje: {total_leads} leads.")
        else:
            await bot.send_message(chat_id=chat_id, text="⚠️ Nenhum lead encontrado na busca.")

    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"❌ Erro durante a busca de leads: {str(e)}")
