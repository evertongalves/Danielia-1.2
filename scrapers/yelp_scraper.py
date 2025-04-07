def search_yelp(termos_busca):
    leads = []
    for termo in termos_busca:
        leads.append({
            'nome': f'Empresa Yelp - {termo}',
            'telefone': 'N/A',
            'origem': 'Yelp',
        })
    return leads
