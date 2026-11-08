import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

sys.stdout.reconfigure(line_buffering=True)
URL = "http://127.0.0.1:8000"


def requisitar(metodo, rota, corpo=None):
    dados = json.dumps(corpo).encode("utf-8") if corpo is not None else None
    req = urllib.request.Request(
        URL + rota, data=dados, method=metodo,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            status, texto = resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as erro:
        status, texto = erro.code, erro.read().decode("utf-8")
    print(f"\n>>> {metodo} {rota}  ->  HTTP {status}")
    print(texto)


def aguardar_servidor(tentativas=50):
    for _ in range(tentativas):
        try:
            socket.create_connection(("127.0.0.1", 8000), timeout=0.2).close()
            return True
        except OSError:
            time.sleep(0.1)
    return False


print("=" * 60)
print("PARTE 1: roteiro de 6 eventos (leitura, falha, sincronização)")
print("=" * 60)
subprocess.run([sys.executable, "main.py"], check=True)

print("\n" + "=" * 60)
print("PARTE 2: consulta e decisão pela API")
print("=" * 60)
servidor = subprocess.Popen([sys.executable, "api.py"], stdout=subprocess.DEVNULL)
try:
    if not aguardar_servidor():
        sys.exit("A API não iniciou na porta 8000 (já tem outro servidor rodando?).")

    requisitar("GET", "/status")
    requisitar("GET", "/eventos")

    decisao = {"id_evento": "VN-004", "decisao": "autorizar", "operador": "op-01"}
    print("\n--- Tentativa por um SENSOR (deve ser negada) ---")
    requisitar("POST", "/decisao", {**decisao, "origem": "posto-vale-norte"})
    print("\n--- Autorização pela CENTRAL/RESGATE (deve ser aceita) ---")
    requisitar("POST", "/decisao", {**decisao, "origem": "central-resgate"})

    requisitar("GET", "/decisoes")
finally:
    servidor.terminate()
    servidor.wait()