import os
import json
from dotenv import load_dotenv

load_dotenv()  # Apenas se você for testar localmente

def testar_variavel_google():
    credentials = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    if not credentials:
        print("❌ Variável GOOGLE_SHEETS_CREDENTIALS **não encontrada**.")
        return

    try:
        cred_dict = json.loads(credentials)
        print("✅ Variável GOOGLE_SHEETS_CREDENTIALS encontrada e carregada com sucesso!")
        print("Project ID:", cred_dict.get("project_id"))
    except json.JSONDecodeError:
        print("⚠️ Variável encontrada, mas o conteúdo não é um JSON válido.")

if __name__ == "__main__":
    testar_variavel_google()
