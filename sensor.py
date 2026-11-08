from datetime import datetime
from risco import classificar_risco

# Roteiro da seção 2.5: (nível cm, chuva mm/h, energia, conexão externa)
# A conexão externa só será usada na Missão 4.
ROTEIRO = [
    (80, 30, 1, "Ativa"),
    (125, 65, 1, "Ativa"),
    (185, 60, 1, "Inativa"),
    (190, 92, 0, "Inativa"),
    (140, 35, 0, "Inativa"),
    (75, 10, 1, "Restabelecida"),
]


class PostoValeNorte:
    """Posto de sensores (SIMULADO: os valores vêm do ROTEIRO)."""

    def __init__(self, nome="Vale Norte"):
        self.nome = nome
        self._contador = 0

    def ler(self, nivel_cm, chuva_mmh, energia):
        self._contador += 1
        return {
            "id_evento": f"VN-{self._contador:03d}",
            "posto": self.nome,
            "data_hora": datetime.now().isoformat(timespec="milliseconds"),
            "nivel_cm": nivel_cm,
            "chuva_mmh": chuva_mmh,
            "energia": energia,
            "risco": classificar_risco(nivel_cm, chuva_mmh),
        }