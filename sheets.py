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

def gerar_relatorio():
    """
    Exemplo de função para gerar relatório.
    Aqui você pode ler dados da planilha e imprimir ou processar como quiser.
    """
    print("🔍 Gerando relatório...")
    client = conectar_sheets()
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_KEY")
    sheet = client.open_by_key(spreadsheet_id).sheet1  # sheet1 é a primeira aba

    dados = sheet.get_all_records()
    print("📊 Relatório de leads:", dados)

def iniciar_prospeccao():
    """
    Exemplo de função para iniciar a prospecção.
    Aqui você poderia simular a coleta de dados e salvar no Google Sheets.
    """
    print("🚀 Iniciando prospecção...")
    # Simulando alguns leads fictícios
    novos_leads = [
        {"Nome": "Cliente Exemplo", "Email": "cliente@exemplo.com", "Telefone": "11999999999"},
        {"Nome": "Outro Cliente", "Email": "outro@cliente.com", "Telefone": "11888888888"}
    ]

    spreadsheet_id = os.getenv("GOOGLE_SHEETS_KEY")
    salvar_leads(novos_leads, spreadsheet_id)
    print("✅ Novos leads salvos com sucesso!")

