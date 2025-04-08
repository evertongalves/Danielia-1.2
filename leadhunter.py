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
    inicio_tempo = datetime.now()
    status_message = await bot.send_message(chat_id=chat_id, text="🚀 Iniciando busca de leads! Isso pode levar alguns minutos...")

    leads_encontrados = []
    ranking_fontes = {}
    progresso = 0
    total_fontes = 8  # Atualize caso adicione mais fontes

    # Lista de scrapers
    scrapers = [
        (search_google_maps, "Google Maps"),
        (search_linkedin, "LinkedIn"),
        (search_instagram, "Instagram"),
        (search_facebook, "Facebook"),
        (search_google_search, "Google Search"),
        (search_yelp, "Yelp"),
        (search_yellow_pages, "Yellow Pages"),
        (search_foursquare, "Foursquare")
    ]

    async def run_scraper(scraper_func, nome_fonte):
        nonlocal progresso
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_message.message_id,
                text=f"🔍 Buscando leads no {nome_fonte}...\n\n⏳ Progresso: {progresso}/{total_fontes} fontes processadas..."
            )

            fonte_leads = await asyncio.to_thread(scraper_func, termos_busca)
            fonte_leads = [lead for lead in fonte_leads if lead.get('email') or lead.get('telefone')]

            if fonte_leads:
                ranking_fontes[nome_fonte] = len(fonte_leads)
                data_hoje = datetime.now().strftime("%Y-%m-%d")
                for lead in fonte_leads:
                    lead['data'] = data_hoje
                    lead['fonte'] = nome_fonte

                leads_encontrados.extend(fonte_leads)

                mensagem_resultado = f"✅ {nome_fonte}: {len(fonte_leads)} leads encontrados."
            else:
                mensagem_resultado = f"⚠️ {nome_fonte}: Nenhum lead encontrado."

        except Exception as e:
            mensagem_resultado = f"❌ {nome_fonte}: Erro ao buscar leads. ({str(e)})"

        progresso += 1
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_message.message_id,
            text=f"{mensagem_resultado}\n\n⏳ Progresso: {progresso}/{total_fontes} fontes processadas..."
        )

    # Executa todos os scrapers em paralelo
    await asyncio.gather(*(run_scraper(func, nome) for func, nome in scrapers))

    # Remove duplicados
    leads_existentes = carregar_leads_existentes()
    leads_filtrados = limpar_duplicados(leads_encontrados, leads_existentes)

    # Salva no Google Sheets
    if leads_filtrados:
        salvar_leads(leads_filtrados)

    tempo_execucao = (datetime.now() - inicio_tempo).total_seconds()
    ranking_ordenado = sorted(ranking_fontes.items(), key=lambda x: x[1], reverse=True)
    ranking_texto = "\n".join([f"{idx+1}. {fonte}: {qtd} leads" for idx, (fonte, qtd) in enumerate(ranking_ordenado)])

    total_encontrados = len(leads_encontrados)
    total_adicionados = len(leads_filtrados)

    mensagem_final = (
        f"📝 Leads salvos no Google Sheets!\n"
        f"💡 Total de {total_adicionados} novos leads adicionados (de {total_encontrados} encontrados).\n\n"
        f"🥇 Ranking das fontes:\n{ranking_texto if ranking_texto else 'Nenhuma fonte gerou leads.'}\n\n"
        f"⏱️ Tempo de execução: {tempo_execucao:.2f} segundos."
    )

    await bot.edit_message_text(chat_id=chat_id, message_id=status_message.message_id, text=mensagem_final)
