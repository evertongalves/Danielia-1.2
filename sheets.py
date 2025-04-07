import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from config import GOOGLE_CREDENTIALS_JSON, GOOGLE_SHEETS_KEY

import json
import os

# Configuração inicial para autenticação
def autenticar_google_sheets():
    # Carrega as credenciais do JSON armazenado na variável de ambiente
    creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON.replace("'", '"'))
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(credentials)
    return client

# Função para garantir que as abas existam
def garantir_abas(sheet):
    abas = [worksheet.title for worksheet in sheet.worksheets()]
    if "Base de Dados" not in abas:
        sheet.add_worksheet(title="Base de Dados", rows="1000", cols="20")
    if "Dashboard" not in abas:
        sheet.add_worksheet(title="Dashboard", rows="1000", cols="20")

# Função de formatação bonita na planilha
def formatar_planilha(sheet):
    try:
        worksheet = sheet.worksheet("Base de Dados")
        # Adiciona cabeçalho, se não existir
        if worksheet.row_count < 1 or not worksheet.row_values(1):
            worksheet.append_row(["Data", "Nome", "Contato", "Status", "Observações"])
    except Exception as e:
        print(f"Erro ao formatar planilha: {e}")

# Função para inserir dados novos
def inserir_dado(sheet, dados):
    worksheet = sheet.worksheet("Base de Dados")
    hoje = datetime.now().strftime("%Y-%m-%d")
    linha = [hoje] + dados
    worksheet.append_row(linha)

# Função de criação de relatório
def gerar_relatorio():
    try:
        client = autenticar_google_sheets()
        sheet = client.open_by_key(GOOGLE_SHEETS_KEY)
        worksheet = sheet.worksheet("Base de Dados")

        # Coleta dados
        registros = worksheet.get_all_values()

        if len(registros) <= 1:
            return "Ainda não há dados suficientes para gerar um relatório. 🚀"

        total_registros = len(registros) - 1  # Subtrai cabeçalho

        # Exemplo simples de contagem por status
        status_col = [row[3] for row in registros[1:]]  # Coluna 'Status'
        status_contagem = {}
        for status in status_col:
            status_contagem[status] = status_contagem.get(status, 0) + 1

        relatorio = [f"📊 Relatório Atualizado ({datetime.now().strftime('%d/%m/%Y')}):", f"• Total de registros: {total_registros}"]

        for status, contagem in status_contagem.items():
            relatorio.append(f"• {status}: {contagem}")

        # Atualiza Dashboard
        atualizar_dashboard(sheet, status_contagem, total_registros)

        return "\n".join(relatorio)

    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        return "❌ Ocorreu um erro ao gerar o relatório."

# Atualiza aba de Dashboard com dados do relatório
def atualizar_dashboard(sheet, status_contagem, total):
    try:
        dashboard = sheet.worksheet("Dashboard")
        dashboard.clear()  # Limpa antes de atualizar

        dashboard.append_row(["Dashboard Visual"])
        dashboard.append_row(["Total de Registros", total])
        dashboard.append_row([""])
        dashboard.append_row(["Status", "Contagem"])

        for status, contagem in status_contagem.items():
            dashboard.append_row([status, contagem])

    except Exception as e:
        print(f"Erro ao atualizar dashboard: {e}")

# Função de prospecção automática (exemplo inicial)
def iniciar_prospeccao():
    try:
        client = autenticar_google_sheets()
        sheet = client.open_by_key(GOOGLE_SHEETS_KEY)
        garantir_abas(sheet)
        formatar_planilha(sheet)

        # Exemplo de prospecção inicial (entrada fictícia para teste)
        dados_teste = ["Contato de Teste", "teste@example.com", "Novo", "Nenhuma observação"]
        inserir_dado(sheet, dados_teste)

        return "🚀 Prospecção automatizada concluída e registrada na planilha!"

    except Exception as e:
        print(f"Erro na prospecção automatizada: {e}")
        return "❌ Erro na prospecção automatizada."

def salvar_leads(leads):
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_JSON)
    client = gspread.authorize(creds)

    try:
        sheet = client.open_by_key(GOOGLE_SHEETS_KEY)
    except Exception:
        sheet = client.create("Leads Automation")
    
    # Sheet Leads
    try:
        leads_sheet = sheet.worksheet("Leads")
    except:
        leads_sheet = sheet.add_worksheet(title="Leads", rows="1000", cols="20")
    
    data = []
    hoje = datetime.now().strftime("%d/%m/%Y")
    for lead in leads:
        data.append([hoje, lead['nome'], lead['telefone'], lead['origem']])
    
    leads_sheet.append_rows(data)

    # Estética automática
    format_leads_sheet(leads_sheet)

    # Dashboard
    try:
        dashboard_sheet = sheet.worksheet("Dashboard")
    except:
        dashboard_sheet = sheet.add_worksheet(title="Dashboard", rows="20", cols="10")
    
    dashboard_sheet.update('A1', 'Relatório de Leads')
    dashboard_sheet.update('A3', 'Total de Leads:')
    dashboard_sheet.update('B3', f"=COUNTA(Leads!B:B)-1")

def format_leads_sheet(sheet):
    set_frozen(sheet, rows=1)
    fmt = cellFormat(
        backgroundColor=color(0.9, 0.9, 0.9),
        textFormat=textFormat(bold=True, foregroundColor=color(0, 0, 0)),
        horizontalAlignment='CENTER'
    )
    format_cell_range(sheet, 'A1:D1', fmt)
    sheet.update('A1', 'Data')
    sheet.update('B1', 'Nome')
    sheet.update('C1', 'Telefone')
    sheet.update('D1', 'Origem')
