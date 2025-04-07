def search_foursquare(termos_busca):
    leads = []
    for termo in termos_busca:
        leads.append({
            'nome': f'Estabelecimento Foursquare - {termo}',
            'telefone': 'N/A',
            'origem': 'Foursquare',
        })
    return leads
