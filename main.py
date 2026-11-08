import os
import sys
import time

from banco import BancoLocal
from broker import BrokerSimulado
from central import CentralEmergencia
from modbus import GatewayModbus
from rede import RedeSimulada, VLAN_SENSORES, VLAN_CENTRAL
from sensor import PostoValeNorte, ROTEIRO
from sincronizador import Sincronizador, CentralExternaSimulada

TOPICO_TELEMETRIA = "farol/vale-norte/telemetria"
TOPICO_ALERTAS = "farol/vale-norte/alertas"
ARQUIVO_BANCO = "farol.db"


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


def ajustar_conexao(sinc, banco, conexao):
    """Aplica a coluna 'conexão externa' do roteiro antes de processar a leitura."""
    if conexao == "Inativa" and sinc.conectado:
        sinc.definir_conexao(False)
        print("  [CONEXÃO] externa INDISPONÍVEL: leituras serão gravadas como pendentes")
    elif conexao == "Restabelecida" and not sinc.conectado:
        pendentes = [e["id_evento"] for e in banco.pendentes()]
        sinc.definir_conexao(True)
        print(f"  [CONEXÃO] externa RESTABELECIDA: sincronizados em ordem {pendentes}")


def mostrar_estado_banco(banco):
    total = len(banco.todos())
    pendentes = len(banco.pendentes())
    print(f"  [BANCO] gravados={total} | pendentes={pendentes} | enviados={total - pendentes}")


# Recria o banco a cada execução (cenário inicial reproduzível)
if os.path.exists(ARQUIVO_BANCO):
    os.remove(ARQUIVO_BANCO)

broker = BrokerSimulado()
central = CentralEmergencia()
broker.assinar(TOPICO_TELEMETRIA, central.receber)
broker.assinar(TOPICO_ALERTAS, central.receber)

gateway = GatewayModbus()
rede = RedeSimulada()
rede.conectar("posto-vale-norte", VLAN_SENSORES)
rede.conectar("central-resgate", VLAN_CENTRAL)

banco = BancoLocal(ARQUIVO_BANCO)
central_externa = CentralExternaSimulada()
sinc = Sincronizador(banco, central_externa)

posto = PostoValeNorte()

# Opcional: "python main.py 4" roda só as 4 primeiras leituras do roteiro
quantidade = int(sys.argv[1]) if len(sys.argv) > 1 else len(ROTEIRO)

for nivel, chuva, energia, conexao in ROTEIRO[:quantidade]:
    ajustar_conexao(sinc, banco, conexao)

    leitura = posto.ler(nivel, chuva, energia)
    print(
        f"{leitura['id_evento']} | {leitura['data_hora']} | "
        f"nível={leitura['nivel_cm']} cm | chuva={leitura['chuva_mmh']} mm/h | "
        f"energia={leitura['energia']} | risco={leitura['risco']}"
    )

    # Rede local: alertas e registradores funcionam mesmo sem conexão externa
    publicar_leitura(broker, leitura)
    gateway.atualizar(leitura)
    consultar_registradores(gateway)

    # Memória local: grava sempre; envia à central externa só se houver conexão
    sinc.processar(leitura)
    mostrar_estado_banco(banco)

    if leitura["id_evento"] == "VN-004":
        demonstrar_permissao(rede, leitura["id_evento"])

    time.sleep(0.2)

n_telemetria = sum(1 for t, _ in broker.historico if t == TOPICO_TELEMETRIA)
n_alertas = sum(1 for t, _ in broker.historico if t == TOPICO_ALERTAS)
print(f"\nResumo: {n_telemetria} publicações de telemetria, {n_alertas} de alertas")
print(f"Tentativas de decisão registradas: {len(rede.tentativas)}")

print("\nHistórico no banco:")
for e in banco.todos():
    print(
        f"  {e['id_evento']} | {e['data_hora']} | "
        f"risco={e['risco']} | sincronização={e['sincronizacao']}"
    )
ids_entregues = [e["id_evento"] for e in central_externa.recebidos]
print(f"Entregues à central externa, em ordem: {ids_entregues}")