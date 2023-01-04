from typing import Dict, List

from .base import BaseQueryBuilder


class CategoryStatsQueryBuilder(BaseQueryBuilder):
    """
    Получаем фичи с узлов и ребер:
        - Столбец id узла
        - Число соседей
        - Число ребер
        - Свойства узла
        - Рассчитываем статистики над числовыми свойствами
        - Счетчики над булевыми и категориальными значениями
    """

    def get_query(self, cat_stats: Dict[str, List[str]], **__) -> List[str]:
        node_sch = self.gschema.node_schema
        edge_sch = self.gschema.edge_schema
        node_label = self.gschema.node_neo4j_label
        edge_label = self.gschema.edge_neo4j_label

        categories_to_calc = []
        for prop in node_sch.properties:
            if prop.is_category:
                categories_to_calc.append(prop.name)

        if not categories_to_calc:
            return None

        columns_to_calc = ["num_neighbours", "num_edges"]

        MATCH_PART = f"MATCH(n:{node_label})-[e:{edge_label}]-(d:{node_label})"
        WITH_FIELDS = [
            f"n.{node_sch.id_property.name} as {node_sch.id_property.name}",
            "count(distinct d) as num_neighbours",
            "count(e) as num_edges",
        ]
        if node_sch.properties:
            for prop in node_sch.properties:
                if (prop.type == int) or (prop.type == float):
                    columns_to_calc.append(prop.name)
                WITH_FIELDS.append(f"n.{prop.name} as {prop.name}")
        if edge_sch.properties:
            for prop in edge_sch.properties:
                if (prop.type == int) or (prop.type == float):
                    features = self.calculate_numeric_features(f"e.{prop.name}", f"e_{prop.name}")
                    WITH_FIELDS.extend(features)
                    for prefix in ["min", "avg", "max", "sum", "median"]:
                        columns_to_calc.append(f"{prefix}_e_{prop.name}")
                elif prop.type == bool:
                    t_col = (
                        f"sum(CASE WHEN e.{prop.name} = true THEN 1 END) as num_true_e_{prop.name}"
                    )
                    f_col = f"sum(CASE WHEN e.{prop.name} = false THEN 1 END) as num_false_e_{prop.name}"
                    WITH_FIELDS.extend([t_col, f_col])
                    columns_to_calc.extend([f"num_true_e_{prop.name}", f"num_false_e_{prop.name}"])
                elif prop.type == str:
                    if prop.is_category:
                        for idx, cat in cat_stats[prop.name]:
                            cat_col = f"sum(CASE WHEN e.{prop.name} = '{cat}' THEN 1 END) as num_{idx}_e_{prop.name}"
                            WITH_FIELDS.append(cat_col)
                            columns_to_calc.append(f"num_{idx}_e_{prop.name}")
                else:
                    raise Exception(f"Unknown type - {prop.type}")
        WITH_PART = f"WITH {', '.join(WITH_FIELDS)}"

        QUERIES = []
        for cat in categories_to_calc:
            RESULT_COLS = ", ".join([f"avg({col}) as avg_{cat}_{col}" for col in columns_to_calc])
            RESULT_PART = f"RETURN {cat}, {RESULT_COLS}"
            QUERY_ROWS = (MATCH_PART, WITH_PART, RESULT_PART)
            QUERIES.append("\n".join(QUERY_ROWS))
        return QUERIES
