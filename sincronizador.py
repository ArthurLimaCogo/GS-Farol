class CentralExternaSimulada:
    """Central externa SIMULADA (só guarda em memória o que recebeu)."""

    def __init__(self):
        self.recebidos = []

    def registrar(self, evento):
        self.recebidos.append(dict(evento))
        return True  # entrega bem-sucedida


class Sincronizador:
    def __init__(self, banco, central_externa):
        self.banco = banco
        self.central_externa = central_externa
        self.conectado = True  # simula a disponibilidade da conexão externa

    def definir_conexao(self, ativa):
        self.conectado = ativa
        if ativa:
            self.sincronizar()  # ao restabelecer, reenvia os pendentes

    def processar(self, leitura):
        """Sempre grava local como pendente; se houver conexão, tenta enviar."""
        self.banco.salvar(leitura, "pendente")
        if self.conectado:
            self.sincronizar()

    def sincronizar(self):
        """Reenvia os pendentes em ordem temporal; marca enviado só após o sucesso."""
        for evento in self.banco.pendentes():
            if not self.conectado:
                break
            if self.central_externa.registrar(dict(evento)):
                self.banco.marcar_enviado(evento["id_evento"])