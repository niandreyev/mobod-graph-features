from typing import List

import pandas as pd
from neo4j import GraphDatabase, Record, Transaction


class DBConnector:
    """Коннектор для получения данных из neo4j"""

    def __init__(self, url: str, port: str, login: str, password: str):
        self._driver = GraphDatabase.driver(f"neo4j://{url}:{port}", auth=(login, password))

    @staticmethod
    def _unpack_query_results(tx: Transaction, query: str) -> List[Record]:
        """Распаковка neo4j.Result в список значений"""
        neo4j_result = tx.run(query)
        records = [record for record in neo4j_result]
        data = []
        for record in records:
            row = [record.get(col) for col in records[0].keys()]
            data.append(row)
        return pd.DataFrame(data, columns=records[0].keys())

    def get_query_result(self, query: str) -> pd.DataFrame:
        """Получение pandas-dataframe из БД по query"""
        with self._driver.session() as session:
            return session.execute_read(DBConnector._unpack_query_results, query=query)
