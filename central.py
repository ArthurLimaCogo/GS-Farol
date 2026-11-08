import json


class CentralEmergencia:
    """Subscriber da central (SIMULADO: recebe mensagens do BrokerSimulado)."""

    def __init__(self):
        self.recebidas = []  # (tópico, dados) de tudo que a central recebeu

    def receber(self, topico, mensagem):
        dados = json.loads(mensagem)
        self.recebidas.append((topico, dados))
        print(
            f"  [CENTRAL] tópico={topico} | posto={dados['posto']} | "
            f"data/hora={dados['data_hora']} | risco={dados['risco']}"
        )