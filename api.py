import json
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

from banco import BancoLocal
from rede import RedeSimulada, VLAN_SENSORES, VLAN_CENTRAL

DECISOES_VALIDAS = ("autorizar", "nao_autorizar")
CAMPOS_OBRIGATORIOS = ("id_evento", "decisao", "operador", "origem")


def criar_servidor(banco, rede, porta=8000):
    """API HTTP REAL (http.server). A origem da requisição é modelada pela
    RedeSimulada (VLANs SIMULADAS): o campo 'origem' do JSON representa o dispositivo."""

    class Handler(BaseHTTPRequestHandler):
        def _responder(self, status, corpo):
            dados = json.dumps(corpo, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(dados)))
            self.end_headers()
            self.wfile.write(dados)

        def do_GET(self):
            if self.path == "/status":
                ultimo = banco.ultimo_evento()
                if ultimo is None:
                    self._responder(404, {"erro": "nenhuma leitura registrada"})
                else:
                    self._responder(200, {"ultima_leitura": dict(ultimo), "risco": ultimo["risco"]})
            elif self.path == "/eventos":
                eventos = [dict(e) for e in banco.todos()]
                self._responder(200, {"total": len(eventos), "eventos": eventos})
            elif self.path == "/decisoes":
                decisoes = [dict(d) for d in banco.decisoes()]
                self._responder(200, {"total": len(decisoes), "decisoes": decisoes})
            else:
                self._responder(404, {"erro": "rota não encontrada"})

        def do_POST(self):
            if self.path != "/decisao":
                self._responder(404, {"erro": "rota não encontrada"})
                return

            try:
                tamanho = int(self.headers.get("Content-Length", 0))
                dados = json.loads(self.rfile.read(tamanho).decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                self._responder(400, {"erro": "JSON inválido"})
                return
            if not isinstance(dados, dict):
                self._responder(400, {"erro": "o corpo deve ser um objeto JSON"})
                return

            faltando = [c for c in CAMPOS_OBRIGATORIOS if not dados.get(c)]
            if faltando:
                self._responder(400, {"erro": "campos obrigatórios ausentes", "campos": faltando})
                return
            if dados["decisao"] not in DECISOES_VALIDAS:
                self._responder(400, {"erro": "decisao deve ser 'autorizar' ou 'nao_autorizar'"})
                return

            evento = banco.buscar_evento(dados["id_evento"])
            if evento is None:
                self._responder(404, {"erro": "evento não encontrado"})
                return
            if evento["risco"] == "NORMAL":
                self._responder(422, {"erro": "o evento não é um alerta (risco NORMAL)"})
                return

            # Verificação de permissão: só a VLAN 20 (central/resgate) registra decisão
            autorizada = rede.solicitar_decisao(
                dados["origem"], f"decisao:{dados['decisao']}", dados["id_evento"]
            )
            registro = {
                "id_evento": dados["id_evento"],
                "decisao": dados["decisao"],
                "operador": dados["operador"],
                "origem": dados["origem"],
                "vlan": rede.vlan_de.get(dados["origem"]),
                "horario": dados.get("horario") or datetime.now().isoformat(timespec="seconds"),
                "resultado": "ACEITA" if autorizada else "NEGADA",
                "motivo": (
                    "solicitação válida da central/resgate (VLAN 20)"
                    if autorizada
                    else "origem sem permissão: somente a VLAN 20 registra decisão"
                ),
            }
            banco.registrar_decisao(registro)  # trilha de auditoria (SQLite)
            self._responder(201 if autorizada else 403, registro)

    return HTTPServer(("127.0.0.1", porta), Handler)


if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    banco = BancoLocal("farol.db")
    rede = RedeSimulada()
    rede.conectar("posto-vale-norte", VLAN_SENSORES)
    rede.conectar("central-resgate", VLAN_CENTRAL)
    servidor = criar_servidor(banco, rede, porta)
    print(f"API FAROL em http://127.0.0.1:{porta}  (Ctrl+C para parar)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")