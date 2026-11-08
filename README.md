# FAROL: GS2 Embedded Systems (FIAP, 2º sem 2026)

Protótipo em Python de uma rede de monitoramento de enchentes (posto Vale Norte,
mensagens, central de emergência, continuidade operacional e decisão humana).

## Requisitos

- Python 3.15.2
- Dependências externas: nenhuma (só biblioteca padrão: json, datetime, sqlite3, http.server)

## Como executar

Dentro da pasta do projeto:

```bash
python demo.py
```

Executa tudo em sequência: o roteiro dos 6 eventos (`main.py`) e depois a API
(`api.py`) com as consultas e decisões. O banco `farol.db` é recriado a cada execução.

Também é possível rodar por partes:

1. `python main.py` roda os 6 eventos (use `python main.py 4` para só os 4 primeiros).
2. `python api.py` sobe a API em http://127.0.0.1:8000 (Ctrl+C para parar).
3. Em outro terminal, consulte a API:

```bash
curl -s http://127.0.0.1:8000/status
curl -s http://127.0.0.1:8000/eventos
curl -s -X POST http://127.0.0.1:8000/decisao -H "Content-Type: application/json" -d '{"id_evento":"VN-004","decisao":"autorizar","operador":"op-01","origem":"central-resgate"}'
curl -s http://127.0.0.1:8000/decisoes
```

## Roteiro de 6 eventos (seção 2.5)

Definido em `sensor.py` (`ROTEIRO`): VN-001 a VN-006. Resultado esperado: 6 registros
locais, 4 alertas (VN-002 a VN-005), 3 eventos pendentes durante a falha (VN-003 a
VN-005) sincronizados uma única vez, registradores após VN-004 em 190 / 92 / 0 / 2,
decisão do sensor negada e da central aceita.

## Real x simulado

| Componente | Arquivo | Situação |
|---|---|---|
| Posto de sensores | `sensor.py` | Simulado (leituras vêm do roteiro) |
| Publisher/broker/subscriber MQTT | `broker.py`, `central.py` | Simulado (modelo didático em Python; não é o protocolo MQTT) |
| Registradores Modbus | `modbus.py` | Simulado (mapa de registradores; não há mensagens Modbus) |
| VLAN 10 e VLAN 20 | `rede.py` | Simulado (regra no código; não é VLAN 802.1Q) |
| Conexão e central externas | `sincronizador.py` | Simulado |
| Energia de reserva | `sensor.py` | Simulado |
| Banco local | `banco.py` | Real (sqlite3) |
| API HTTP | `api.py` | Real (http.server) |

## Arquivos

`risco.py` · `sensor.py` · `broker.py` · `central.py` · `modbus.py` · `rede.py` ·
`banco.py` · `sincronizador.py` · `api.py` · `main.py` · `demo.py`