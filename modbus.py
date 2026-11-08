class GatewayModbus:
    """Mapa Modbus VIRTUAL (modelo didático; não implementa mensagens Modbus reais)."""

    CODIGO_RISCO = {"NORMAL": 0, "ATENÇÃO": 1, "CRÍTICO": 2}

    def __init__(self):
        self.registradores = {40001: 0, 40002: 0, 40003: 0, 40004: 0}

    def atualizar(self, leitura):
        self.registradores[40001] = leitura["nivel_cm"]
        self.registradores[40002] = leitura["chuva_mmh"]
        self.registradores[40003] = leitura["energia"]
        self.registradores[40004] = self.CODIGO_RISCO[leitura["risco"]]

    def ler(self, endereco):
        if endereco not in self.registradores:
            raise KeyError(f"Endereço Modbus inexistente: {endereco}")
        return self.registradores[endereco]