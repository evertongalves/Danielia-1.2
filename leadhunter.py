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
    start_time = time.time()  # ⏱️ Timer start

    await bot.send_message(chat_id=chat_id, text="🚀 Iniciando busca de leads! Isso pode levar alguns minutos...")

    leads_encontrados = []
    ranking_fontes = {}
    total_fontes = 8
    fontes_processadas = 0

    # Mensagem de progresso inicial
    progresso_msg = await bot.send_message(chat_id=chat_id, text=f"⏳ Progresso: 0/{total_fontes} fontes processadas...")

    fontes = [
        ("Google Maps", search_google_maps),
        ("LinkedIn", search_linkedin),
        ("Instagram", search_instagram),
        ("Facebook", search_facebook),
        ("Google Search", search_google_search),
        ("Yelp", search_yelp),
        ("Yellow Pages", search_yellow_pages),
        ("Foursquare", search_foursquare),
    ]

    async def run_scraper(scraper_func, nome_fonte):
        nonlocal fontes_processadas
        await bot.send_message(chat_id=chat_id, text=f"🔍 Buscando leads no {nome_fonte}...")

        try:
            fonte_leads = await asyncio.to_thread(scraper_func, termos_busca)
            # Filtra leads válidos
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
            await bot.send_message(chat_id=chat_id, text=f"❌ Erro ao buscar no {nome_fonte}: {e}")

        fontes_processadas += 1
        await progresso_msg.edit_text(f"⏳ Progresso: {fontes_processadas}/{total_fontes} fontes processadas...")

    # Executa todas as fontes em sequência
    for nome_fonte, scraper_func in fontes:
        await run_scraper(scraper_func, nome_fonte)

    # Remove duplicados
    leads_existentes = carregar_leads_existentes()
    leads_unicos = limpar_duplicados(leads_encontrados, leads_existentes)

    # Salva no Google Sheets
    if leads_unicos:
        salvar_leads(leads_unicos)

    elapsed_time = time.time() - start_time  # ⏱️ Timer end
    minutos, segundos = divmod(int(elapsed_time), 60)

    # Ranking das fontes
    if ranking_fontes:
        ranking_texto = "\n".join([f"{i + 1}️⃣ {fonte}: {qtd} leads" for i, (fonte, qtd) in enumerate(sorted(ranking_fontes.items(), key=lambda x: x[1], reverse=True))])
    else:
        ranking_texto = "Nenhuma fonte retornou leads."

    # Mensagem final
    await bot.send_message(
        chat_id=chat_id,
        text=(
            "📝 Leads salvos no Google Sheets!\n"
            f"💡 Total de {len(leads_unicos)} novos leads adicionados (de {len(leads_encontrados)} encontrados).\n\n"
            f"🥇 Ranking das fontes:\n{ranking_texto}\n\n"
            f"⏱️ Tempo total: {minutos} min {segundos} seg"
        )
    )

except Exception as e:
    await bot.send_message(chat_id=chat_id, text=f"❌ Ocorreu um erro durante a busca de leads: {e}")
