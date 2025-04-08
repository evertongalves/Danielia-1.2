import json
import os
import gspread
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()

def carregar_credenciais():
    """Carrega as credenciais do Google Sheets da variável de ambiente ou de um arquivo JSON."""
    credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    
    if not credentials_json:
        raise ValueError("Credenciais do Google Sheets não encontradas na variável de ambiente.")
    
    try:
        credentials = json.loads(credentials_json)
    except json.JSONDecodeError as e:
        raise ValueError("Erro ao decodificar as credenciais JSON.") from e

    return credentials

def conectar_sheets():
    """Cria a conexão com o Google Sheets."""
    credentials = carregar_credenciais()
    client = gspread.service_account_from_dict(credentials)
    return client

def salvar_leads(leads, spreadsheet_id, sheet_name='Sheet1'):
    """
    Salva uma lista de leads no Google Sheets.
    
    :param leads: Lista de dicionários contendo os dados dos leads.
    :param spreadsheet_id: ID da planilha do Google Sheets.
    :param sheet_name: Nome da aba da planilha (padrão: 'Sheet1').
    """
    if not leads:
        print("Nenhum lead para salvar.")
        return

    client = conectar_sheets()
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)

    header = sheet.row_values(1)

    rows = []
    for lead in leads:
        row = [lead.get(col, '') for col in header]
        rows.append(row)

    sheet.append_rows(rows, value_input_option='USER_ENTERED')
    print(f"{len(rows)} leads salvos com sucesso no Google Sheets!")

def gerar_relatorio():
    """
    Exemplo de função para gerar relatório.
    """
    print("🔍 Gerando relatório...")
    client = conectar_sheets()
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_KEY")
    sheet = client.open_by_key(spreadsheet_id).sheet1

    data = sheet.get_all_records()
    print(f"Total de registros encontrados: {len(data)}")
    for i, record in enumerate(data, start=1):
        print(f"{i}: {record}")

def iniciar_prospeccao():
    """
    Função para iniciar o processo de prospecção de leads.
    """
    print("🚀 Iniciando prospecção de leads...")
    
    client = conectar_sheets()
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_KEY")
    sheet = client.open_by_key(spreadsheet_id).sheet1

    data = sheet.get_all_records()

    if not data:
        print("⚠️ Nenhum lead encontrado para prospecção.")
        return

    for lead in data:
        print(f"Prospectando lead: {lead}")
        # Aqui você pode integrar com sua automação de envio, por exemplo.
        # Enviar mensagem, e-mail, webhook, etc.

    print("✅ Prospecção finalizada com sucesso.")
