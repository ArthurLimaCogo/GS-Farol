import sqlite3


class BancoLocal:
    """Memória local em SQLite (REAL: usa a biblioteca sqlite3)."""

    def __init__(self, caminho="farol.db"):
        self.conn = sqlite3.connect(caminho)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS eventos (
                id_evento     TEXT PRIMARY KEY,
                posto         TEXT NOT NULL,
                data_hora     TEXT NOT NULL,
                nivel_cm      INTEGER NOT NULL,
                chuva_mmh     INTEGER NOT NULL,
                energia       INTEGER NOT NULL,
                risco         TEXT NOT NULL,
                sincronizacao TEXT NOT NULL DEFAULT 'pendente'
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS decisoes (
                id_decisao INTEGER PRIMARY KEY AUTOINCREMENT,
                id_evento  TEXT NOT NULL,
                decisao    TEXT NOT NULL,
                operador   TEXT NOT NULL,
                origem     TEXT NOT NULL,
                vlan       INTEGER,
                horario    TEXT NOT NULL,
                resultado  TEXT NOT NULL,
                motivo     TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def salvar(self, leitura, sincronizacao="pendente"):
        self.conn.execute(
            """
            INSERT INTO eventos
                (id_evento, posto, data_hora, nivel_cm, chuva_mmh,
                 energia, risco, sincronizacao)
            VALUES
                (:id_evento, :posto, :data_hora, :nivel_cm, :chuva_mmh,
                 :energia, :risco, :sincronizacao)
            """,
            {**leitura, "sincronizacao": sincronizacao},
        )
        self.conn.commit()

    def pendentes(self):
        """Eventos ainda não sincronizados, em ordem temporal."""
        return self.conn.execute(
            "SELECT * FROM eventos WHERE sincronizacao = 'pendente' "
            "ORDER BY data_hora, id_evento"
        ).fetchall()

    def marcar_enviado(self, id_evento):
        """Só altera se ainda estiver pendente; devolve quantas linhas mudaram."""
        cursor = self.conn.execute(
            "UPDATE eventos SET sincronizacao = 'enviado' "
            "WHERE id_evento = ? AND sincronizacao = 'pendente'",
            (id_evento,),
        )
        self.conn.commit()
        return cursor.rowcount

    def todos(self):
        return self.conn.execute(
            "SELECT * FROM eventos ORDER BY data_hora, id_evento"
        ).fetchall()

    def buscar_evento(self, id_evento):
        return self.conn.execute(
            "SELECT * FROM eventos WHERE id_evento = ?", (id_evento,)
        ).fetchone()

    def ultimo_evento(self):
        return self.conn.execute(
            "SELECT * FROM eventos ORDER BY data_hora DESC, id_evento DESC LIMIT 1"
        ).fetchone()

    def registrar_decisao(self, d):
        """Guarda a decisão e o resultado (trilha de auditoria)."""
        self.conn.execute(
            """
            INSERT INTO decisoes
                (id_evento, decisao, operador, origem, vlan, horario, resultado, motivo)
            VALUES
                (:id_evento, :decisao, :operador, :origem, :vlan, :horario, :resultado, :motivo)
            """,
            d,
        )
        self.conn.commit()

    def decisoes(self):
        return self.conn.execute("SELECT * FROM decisoes ORDER BY id_decisao").fetchall()