from datetime import datetime

VLAN_SENSORES = 10
VLAN_CENTRAL = 20


class RedeSimulada:
    """VLANs SIMULADAS por regra no código (modelo didático; não é VLAN 802.1Q real)."""

    def __init__(self):
        self.vlan_de = {}      # dispositivo -> número da VLAN
        self.tentativas = []   # registro de TODAS as tentativas (aceitas e negadas)

    def conectar(self, dispositivo, vlan):
        self.vlan_de[dispositivo] = vlan

    def solicitar_decisao(self, origem, acao, id_evento):
        """Só a VLAN 20 (central/resgate) pode registrar decisão de atendimento."""
        vlan = self.vlan_de.get(origem)
        autorizada = (vlan == VLAN_CENTRAL)
        self.tentativas.append({
            "data_hora": datetime.now().isoformat(timespec="milliseconds"),
            "origem": origem,
            "vlan": vlan,
            "acao": acao,
            "id_evento": id_evento,
            "resultado": "AUTORIZADA" if autorizada else "NEGADA",
        })
        return autorizada