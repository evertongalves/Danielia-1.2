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
    
    # Converter a string JSON para dicionário
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

    # Obter cabeçalhos da primeira linha da planilha
    header = sheet.row_values(1)

    # Preparar dados para inserção
    rows = []
    for lead in leads:
        row = [lead.get(col, '') for col in header]
        rows.append(row)

    # Adicionar linhas na planilha
    sheet.append_rows(rows, value_input_option='USER_ENTERED')
    print(f"{len(rows)} leads salvos com sucesso no Google Sheets!")
