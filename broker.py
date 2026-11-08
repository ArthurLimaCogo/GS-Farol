import json


class BrokerSimulado:
    """Broker MQTT SIMULADO (modelo didático em Python; não é o protocolo MQTT real)."""

    def __init__(self):
        self._assinantes = {}  # tópico -> lista de funções que recebem a mensagem
        self.historico = []    # (tópico, mensagem JSON) de tudo que foi publicado

    def assinar(self, topico, callback):
        self._assinantes.setdefault(topico, []).append(callback)

    def publicar(self, topico, payload):
        mensagem = json.dumps(payload, ensure_ascii=False)  # mensagens em JSON
        self.historico.append((topico, mensagem))
        for callback in self._assinantes.get(topico, []):
            callback(topico, mensagem)