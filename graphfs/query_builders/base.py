from typing import List

from ..schema import GraphSchema


class BaseQueryBuilder:
    """Базовый класс для построения запросов к БД"""

    def __init__(self, gschema: GraphSchema) -> None:
        self.gschema = gschema

    @staticmethod
    def calculate_numeric_features(property: str, alias: str) -> List[str]:
        functions_and_prefixes = [
            ("min", ")", "min"),
            ("avg", ")", "avg"),
            ("max", ")", "max"),
            ("sum", ")", "sum"),
            ("percentileDisc", ", 0.5)", "median"),
        ]
        features = []
        for func_p1, func_p2, prefix in functions_and_prefixes:
            feature = f"{func_p1}({property}{func_p2} as {prefix}_{alias}"
            features.append(feature)
        return features

    def get_cat_stats_query(self) -> List[str]:
        node_sch = self.gschema.node_schema
        MATCH_PART = f"MATCH(n:{self.gschema.node_neo4j_label})\n"
        QUERIES = []
        for prop in node_sch.properties:
            if prop.is_category:
                RESULT_PART = f"RETURN distinct n.{prop.name} as {prop.name}"
                QUERIES.append((prop.name, f"{MATCH_PART}{RESULT_PART}"))
        return QUERIES

    def get_query(self, **__) -> str:
        """Построить запрос"""
        raise NotImplementedError()
