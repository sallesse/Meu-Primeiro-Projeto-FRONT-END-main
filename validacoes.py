import re


def validar_placa(placa):
    """Valida se a placa tem formato correto (padrão antigo ou Mercosul)."""
    placa = placa.strip().upper().replace('-', '').replace(' ', '')
    
    padrao_antigo = r'^[A-Z]{3}[0-9]{4}$'      # ex: ABC1234
    padrao_mercosul = r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$'  # ex: ABC1D23
    
    return bool(re.match(padrao_antigo, placa) or re.match(padrao_mercosul, placa))


def placa_ja_cadastrada(placa, veiculos):
    """Verifica se a placa já está cadastrada numa lista de veículos."""
    placa = placa.strip().upper().replace('-', '').replace(' ', '')
    for v in veiculos:
        placa_salva = v.get('placa', '').strip().upper().replace('-', '').replace(' ', '')
        if placa_salva == placa:
            return True
    return False





