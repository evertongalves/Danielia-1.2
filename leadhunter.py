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
        total_fontes = 8
        fontes_processadas = 0

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

        # Mensagem de progresso inicial
        progresso_msg = await bot.send_message(chat_id=chat_id, text="⏳ Progresso: 0/8 fontes processadas...")

        async def atualizar_progresso():
            loading = "." * (fontes_processadas % 4)  # Vai de 0 a 3 pontinhos
            await progresso_msg.edit_text(f"⏳ Progresso: {fontes_processadas}/{total_fontes} fontes processadas{loading}")

        for nome_fonte, scraper_func in fontes:
            await atualizar_progresso()
            await bot.send_message(chat_id=chat_id, text=f"🔍 Buscando leads no {nome_fonte}...")

            try:
                fonte_leads = await asyncio.to_thread(scraper_func, termos_busca)
                fonte_leads = [lead for lead in fonte_leads if lead.get('email') or lead.get('telefone')]

                if fonte_leads:
                    # Atualiza ranking
                    ranking_fontes[nome_fonte] = len(fonte_leads)

                    # Adiciona metadados
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
            await atualizar_progresso()

        # Finaliza progresso
        await progresso_msg.edit_text(f"✅ Progresso concluído: {fontes_processadas}/{total_fontes} fontes processadas.")

        # Limpeza de duplicados
        leads_existentes = carregar_leads_existentes()
        leads_filtrados = limpar_duplicados(leads_encontrados, leads_existentes)

        # Salva no Sheets
        if leads_filtrados:
            salvar_leads(leads_filtrados)
            total_encontrados = len(leads_filtrados)
            await bot.send_message(chat_id=chat_id, text=f"📝 Leads salvos no Google Sheets!\n💡 Total de {total_encontrados} novos leads adicionados (de {len(leads_encontrados)} encontrados).")
        else:
            await bot.send_message(chat_id=chat_id, text="💡 Nenhum novo lead para adicionar (todos eram duplicados).")

        # Ranking final
        if ranking_fontes:
            ranking_texto = "\n".join(
                [f"🥇 {fonte}: {quantidade} leads" for fonte, quantidade in sorted(ranking_fontes.items(), key=lambda x: x[1], reverse=True)]
            )
            await bot.send_message(chat_id=chat_id, text=f"📊 Ranking das fontes:\n{ranking_texto}")

        await bot.send_message(chat_id=chat_id, text="✅ Busca de leads finalizada!")

    except Exception as e:
        await bot.send_message(chat_id=chat_id, text=f"❌ Erro durante a busca de leads: {str(e)}")
