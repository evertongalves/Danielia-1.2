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
    sheet = client.open_by_key(spreadsheet_id).worksheet('Sheet1')
    
    # Ler todos os registros
    records = sheet.get_all_records()
    print(f"Total de registros encontrados: {len(records)}")
    for record in records:
        print(record)

def iniciar_prospeccao():
    """
    Exemplo de função para iniciar uma prospecção.
    Aqui você poderia adicionar lógica para buscar novos leads ou enviar mensagens.
    """
    print("🚀 Iniciando prospecção...")
    # Simulação de operação
    # Exemplo: buscar novos dados de API ou banco de dados
    novos_leads = [
        {"Nome": "João Silva", "Email": "joao@example.com", "Telefone": "11999999999"},
        {"Nome": "Maria Souza", "Email": "maria@example.com", "Telefone": "11988888888"}
    ]
    spreadsheet_id = os.getenv("GOOGLE_SHEETS_KEY")
    salvar_leads(novos_leads, spreadsheet_id)

def iniciar_prospeccao():
    """
    Inicia a prospecção de leads.
    """
    print("🚀 Iniciando prospecção de leads...")

    # Define o chat_id manualmente para testar (depois podemos dinamizar)
    chat_id = '757625546'  # Substitua pelo seu chat_id do Telegram
    termos_busca = 'barbearia são paulo'  # Pode colocar os termos que quiser para o teste

    asyncio.run(leadhunter_handler(chat_id, termos_busca))

def carregar_leads_existentes():
    gc = gspread.service_account(filename='credentials.json')
    sh = gc.open(GOOGLE_SHEET_NAME)
    worksheet = sh.sheet1
    leads_existentes = worksheet.get_all_records()

    # Convertemos em um set de tuplas para facilitar verificação de duplicados
    leads_existentes_set = set()
    for lead in leads_existentes:
        chave = (lead.get('email', '').lower(), lead.get('telefone', '').replace(" ", "").replace("-", ""))
        leads_existentes_set.add(chave)

    return leads_existentes_set
