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