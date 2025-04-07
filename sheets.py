import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from config import GOOGLE_CREDENTIALS_JSON, GOOGLE_SHEETS_KEY
from collections import Counter
import json

# Autenticação Google Sheets
def autenticar_google_sheets():
    creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON.replace("'", '"'))
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(credentials)
    return client

# Garantir abas necessárias
def garantir_abas(sheet):
    abas = [ws.title for ws in sheet.worksheets()]
    if "Base de Dados" not in abas:
        sheet.add_worksheet(title="Base de Dados", rows="1000", cols="20")
    if "Dashboard" not in abas:
        sheet.add_worksheet(title="Dashboard", rows="1000", cols="20")

# Formatação bonita da planilha
def formatar_planilha(sheet):
    try:
        worksheet = sheet.worksheet("Base de Dados")
        header = ["Data", "Fonte", "Empresa", "Telefone", "Email", "Website", "Observações"]
        linhas_existentes = worksheet.get_all_values()

        # Se estiver vazio, adiciona cabeçalho
        if not linhas_existentes:
            worksheet.append_row(header)

        # Formatação visual (cor de fundo nas colunas)
        formatacoes = [
            {"range": "A:A", "color": (211, 211, 211)},  # Cinza claro - Data
            {"range": "B:B", "color": (135, 206, 250)},  # Azul claro - Fonte
            {"range": "C:C", "color": (173, 216, 230)},  # Azul claro - Empresa
            {"range": "D:D", "color": (144, 238, 144)},  # Verde claro - Telefone
            {"range": "E:E", "color": (144, 238, 144)},  # Verde claro - Email
            {"range": "F:F", "color": (255, 228, 181)},  # Amarelo claro - Website
            {"range": "G:G", "color": (255, 182, 193)},  # Rosa claro - Observações
        ]

        from gspread_formatting import CellFormat, Color, format_cell_range

        for item in formatacoes:
            cell_format = CellFormat(
                backgroundColor=Color(*(c / 255 for c in item["color"]))
            )
            format_cell_range(worksheet, item["range"], cell_format)

    except Exception as e:
        print(f"Erro ao formatar planilha: {e}")

# Inserir dados novos
def inserir_dado(sheet, dados):
    worksheet = sheet.worksheet("Base de Dados")
    hoje = datetime.now().strftime("%Y-%m-%d")
    linha = [hoje] + dados
    worksheet.append_row(linha)
    atualizar_dashboard(sheet)

# Atualizar dashboard visual
def atualizar_dashboard(sheet):
    try:
        worksheet = sheet.worksheet("Base de Dados")
        dashboard = sheet.worksheet("Dashboard")

        registros = worksheet.get_all_values()
        if len(registros) <= 1:
            dashboard.clear()
            dashboard.update('A1', [["Ainda não há dados suficientes para o Dashboard 🚀"]])
            return

        headers = registros[0]
        dados = registros[1:]

        total_leads = len(dados)
        fontes = [linha[1] for linha in dados]
        contagem_fontes = Counter(fontes)

        dashboard.clear()

        dashboard.update('A1', [["📊 Dashboard de Leads"]])
        dashboard.update('A3', [["Total de Leads", total_leads]])

        dashboard.update('A5', [["Leads por Fonte"]])
        dashboard.update('A6', [["Fonte", "Quantidade"]])
        for i, (fonte, quantidade) in enumerate(contagem_fontes.items(), start=7):
            dashboard.update(f"A{i}:B{i}", [[fonte, quantidade]])

        dashboard.update('D5', [["Evolução Diária"]])
        datas = [linha[0] for linha in dados]
        contagem_datas = Counter(datas)
        dashboard.update('D6', [["Data", "Quantidade"]])
        for i, (data, quantidade) in enumerate(sorted(contagem_datas.items()), start=7):
            dashboard.update(f"D{i}:E{i}", [[data, quantidade]])

        dashboard.update('G5', [["Gráfico de Pizza (manual)"]])
        dashboard.update('G6', [["Fonte", "Quantidade"]])
        for i, (fonte, quantidade) in enumerate(contagem_fontes.items(), start=7):
            dashboard.update(f"G{i}:H{i}", [[fonte, quantidade]])

    except Exception as e:
        print(f"Erro ao atualizar Dashboard: {e}")

# Gerar relatório básico (usado no /relatorio)
def gerar_relatorio():
    try:
        client = autenticar_google_sheets()
        sheet = client.open_by_key(GOOGLE_SHEETS_KEY)
        worksheet = sheet.worksheet("Base de Dados")

        registros = worksheet.get_all_values()
        if len(registros) <= 1:
            return "Ainda não há dados suficientes para gerar um relatório. 🚀"

        total_registros = len(registros) - 1  # Desconta o cabeçalho
        fontes = [linha[1] for linha in registros[1:]]
        contagem_fontes = Counter(fontes)

        relatorio = f"📊 Relatório Atualizado\n\nTotal de Leads: {total_registros}\n\nLeads por Fonte:\n"
        for fonte, quantidade in contagem_fontes.items():
            relatorio += f"- {fonte}: {quantidade}\n"

        return relatorio

    except Exception as e:
        return f"Erro ao gerar relatório: {e}"
