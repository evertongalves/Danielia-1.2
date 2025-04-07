def search_facebook(termos_busca):
    leads = []
    for termo in termos_busca:
        leads.append({
            'nome': f'Página Facebook - {termo}',
            'telefone': 'N/A',
            'origem': 'Facebook',
        })
    return leads
