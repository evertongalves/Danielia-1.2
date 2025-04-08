import asyncio
from datetime import datetime
import time
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
    start_time = time.time()

    await bot.send_message(chat_id=chat_id, text="🚀 Iniciando busca de leads! Isso pode levar alguns minutos...")

    leads_encontrados = []
    ranking_fontes = {}
    total_fontes = 8
    fontes_processadas = 0

    # Mensagem de progresso inicial
    progresso_msg = await bot.send_message(chat_id=chat_id, text=f"⏳ Progresso: {fontes_processadas}/{total_fontes} fontes processadas...")

    # Mapeamento das funções e nomes
    scrapers = [
        (search_google_maps, "Google Maps"),
        (search_linkedin, "LinkedIn"),
        (search_instagram, "Instagram"),
        (search_facebook, "Facebook"),
        (search_google_search, "Google Search"),
        (search_yelp, "Yelp"),
        (search_yellow_pages, "Yellow Pages"),
        (search_foursquare, "Foursquare"),
    ]

    # Carrega leads existentes
    leads_existentes = carregar_leads_existentes()

    # Função para rodar cada scraper individualmente
    async def run_scraper(scraper_func, nome_fonte):
        nonlocal fontes_processadas, leads_encontrados

        await bot.send_message(chat_id=chat_id, text=f"🔍 Buscando leads no {nome_fonte}...")
        try:
            fonte_leads = await asyncio.to_thread(scraper_func, termos_busca)
            fonte_leads = [lead for lead in fonte_leads if lead.get('email') or lead.get('telefone')]

            if fonte_leads:
                ranking_fontes[nome_fonte] = len(fonte_leads)

                data_hoje = datetime.now().strftime("%Y-%m-%d")
                for lead in fonte_leads:
                    lead['data'] = data_hoje
                    lead['fonte'] = nome_fonte

                leads_encontrados.extend(fonte_leads)
                await bot.send_message(chat_id=chat_id, text=f"✅ {nome_fonte}: {len(fonte_leads)} leads encontrados.")
            else:
                await bot.send_message(chat_id=chat_id, text=f"⚠️ {nome_fonte}: Nenhum lead encontrado.")

        except Exception as e:
            await bot.send_message(chat_id=chat_id, text=f"❌ Erro ao buscar no {nome_fonte}: {str(e)}")

        fontes_processadas += 1
        await progresso_msg.edit_text(f"⏳ Progresso: {fontes_processadas}/{total_fontes} fontes processadas...")

    # Executa todas as fontes em paralelo
    await asyncio.gather(*(run_scraper(scraper_func, nome_fonte) for scraper_func, nome_fonte in scrapers))

    # Remove duplicados
    leads_filtrados = limpar_duplicados(leads_encontrados, leads_existentes)

    # Salva leads
    salvar_leads(leads_filtrados)

    elapsed_time = time.time() - start_time
    minutos, segundos = divmod(int(elapsed_time), 60)

    # Prepara ranking das fontes
    ranking_texto = "\n".join(
        [f"{i+1}️⃣ {fonte}: {quantidade} leads" for i, (fonte, quantidade) in enumerate(
            sorted(ranking_fontes.items(), key=lambda x: x[1], reverse=True)
        )]
    ) or "Nenhuma fonte retornou leads."

    # Mensagem final
    await bot.send_message(
        chat_id=chat_id,
        text=(
            "📝 Leads salvos no Google Sheets!\n"
            f"💡 Total de {len(leads_filtrados)} novos leads adicionados (de {len(leads_encontrados)} encontrados).\n\n"
            f"⏱️ Tempo total: {minutos}m {segundos}s\n\n"
            f"🥇 Ranking das fontes:\n{ranking_texto}"
        )
    )
