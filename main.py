import sys
import time

from broker import BrokerSimulado
from central import CentralEmergencia
from modbus import GatewayModbus
from rede import RedeSimulada, VLAN_SENSORES, VLAN_CENTRAL
from sensor import PostoValeNorte, ROTEIRO

TOPICO_TELEMETRIA = "farol/vale-norte/telemetria"
TOPICO_ALERTAS = "farol/vale-norte/alertas"


def publicar_leitura(broker, leitura):
    """Telemetria recebe todas as leituras; alertas só ATENÇÃO e CRÍTICO."""
    broker.publicar(TOPICO_TELEMETRIA, leitura)
    if leitura["risco"] != "NORMAL":
        broker.publicar(TOPICO_ALERTAS, leitura)


def consultar_registradores(gateway):
    valores = ", ".join(f"{a}={gateway.ler(a)}" for a in (40001, 40002, 40003, 40004))
    print(f"  [MODBUS] {valores}")


def demonstrar_permissao(rede, id_evento):
    print(f"\n  --- Verificação de permissão ({id_evento}) ---")
    for origem in ("posto-vale-norte", "central-resgate"):
        rede.solicitar_decisao(origem, "ligar_bomba", id_evento)
        t = rede.tentativas[-1]
        print(
            f"  [REDE] origem={origem} | VLAN={t['vlan']} | "
            f"ação={t['acao']} | resultado={t['resultado']}"
        )
    print()


broker = BrokerSimulado()
central = CentralEmergencia()
broker.assinar(TOPICO_TELEMETRIA, central.receber)
broker.assinar(TOPICO_ALERTAS, central.receber)

gateway = GatewayModbus()
rede = RedeSimulada()
rede.conectar("posto-vale-norte", VLAN_SENSORES)
rede.conectar("central-resgate", VLAN_CENTRAL)

posto = PostoValeNorte()

# Opcional: "python main.py 4" roda só as 4 primeiras leituras do roteiro
quantidade = int(sys.argv[1]) if len(sys.argv) > 1 else len(ROTEIRO)

for nivel, chuva, energia, _conexao in ROTEIRO[:quantidade]:
    leitura = posto.ler(nivel, chuva, energia)
    print(
        f"{leitura['id_evento']} | {leitura['data_hora']} | "
        f"nível={leitura['nivel_cm']} cm | chuva={leitura['chuva_mmh']} mm/h | "
        f"energia={leitura['energia']} | risco={leitura['risco']}"
    )
    publicar_leitura(broker, leitura)
    gateway.atualizar(leitura)
    consultar_registradores(gateway)

    if leitura["id_evento"] == "VN-004":
        demonstrar_permissao(rede, leitura["id_evento"])

    time.sleep(0.2)

n_telemetria = sum(1 for t, _ in broker.historico if t == TOPICO_TELEMETRIA)
n_alertas = sum(1 for t, _ in broker.historico if t == TOPICO_ALERTAS)
print(f"\nResumo: {n_telemetria} publicações de telemetria, {n_alertas} de alertas")
print(f"Tentativas de decisão registradas: {len(rede.tentativas)}")