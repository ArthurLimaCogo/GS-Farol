def classificar_risco(nivel_cm, chuva_mmh):
    """Avalia CRÍTICO primeiro, depois ATENÇÃO, senão NORMAL."""
    if nivel_cm >= 180 or chuva_mmh >= 90:
        return "CRÍTICO"
    if nivel_cm >= 120 or chuva_mmh >= 60:
        return "ATENÇÃO"
    return "NORMAL"