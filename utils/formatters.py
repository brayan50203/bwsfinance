def format_brl(value):
    """Formata numero para moeda brasileira (R$)"""
    if value is None:
        return "0,00"
    try:
        value = float(value)
        # Formata com separadores: 1234567.89 -> 1,234,567.89
        formatted = f"{value:,.2f}"
        # Troca separadores para padrão BR: 1.234.567,89
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
        return formatted
    except (ValueError, TypeError):
        return "0,00"
