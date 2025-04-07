def search_yellow_pages(termos_busca):
    leads = []
    for termo in termos_busca:
        leads.append({
            'nome': f'Contato Yellow Pages - {termo}',
            'telefone': 'N/A',
            'origem': 'Yellow Pages',
        })
    return leads
