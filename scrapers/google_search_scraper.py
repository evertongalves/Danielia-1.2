import requests
from bs4 import BeautifulSoup

def search_google_search(termos_busca):
    leads = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for termo in termos_busca:
        query = termo.replace(' ', '+') + "+telefone"
        url = f"https://www.google.com/search?q={query}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        snippets = soup.select('div.BNeawe.s3v9rd.AP7Wnd')

        for snippet in snippets:
            text = snippet.get_text()
            if 'tel' in text.lower() or any(char.isdigit() for char in text):
                leads.append({
                    'nome': f'Resultado Google - {termo}',
                    'telefone': text,
                    'origem': 'Google Search',
                })
    return leads
