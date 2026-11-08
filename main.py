import sys
import time

from broker import BrokerSimulado
from central import CentralEmergencia
from sensor import PostoValeNorte, ROTEIRO

TOPICO_TELEMETRIA = "farol/vale-norte/telemetria"
TOPICO_ALERTAS = "farol/vale-norte/alertas"


def publicar_leitura(broker, leitura):
    """Telemetria recebe todas as leituras; alertas só ATENÇÃO e CRÍTICO."""
    broker.publicar(TOPICO_TELEMETRIA, leitura)
    if leitura["risco"] != "NORMAL":
        broker.publicar(TOPICO_ALERTAS, leitura)


broker = BrokerSimulado()
central = CentralEmergencia()
broker.assinar(TOPICO_TELEMETRIA, central.receber)
broker.assinar(TOPICO_ALERTAS, central.receber)

posto = PostoValeNorte()

# Opcional: "python main.py 3" roda só as 3 primeiras leituras do roteiro
quantidade = int(sys.argv[1]) if len(sys.argv) > 1 else len(ROTEIRO)

for nivel, chuva, energia, _conexao in ROTEIRO[:quantidade]:
    leitura = posto.ler(nivel, chuva, energia)
    print(
        f"{leitura['id_evento']} | {leitura['data_hora']} | "
        f"nível={leitura['nivel_cm']} cm | chuva={leitura['chuva_mmh']} mm/h | "
        f"energia={leitura['energia']} | risco={leitura['risco']}"
    )
    publicar_leitura(broker, leitura)
    time.sleep(0.2)

n_telemetria = sum(1 for t, _ in broker.historico if t == TOPICO_TELEMETRIA)
n_alertas = sum(1 for t, _ in broker.historico if t == TOPICO_ALERTAS)
print(f"\nResumo: {n_telemetria} publicações de telemetria, {n_alertas} de alertas")