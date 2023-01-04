from typing import Dict, List

from .base import BaseQueryBuilder


class NodesStatsQueryBuilder(BaseQueryBuilder):
    """
    Получаем фичи с узлов и ребер:
        - Столбец id узла
        - Число соседей
        - Число ребер
        - Свойства узла
        - Рассчитываем статистики над числовыми свойствами
        - Счетчики над булевыми и категориальными значениями
    """

    def get_query(self, cat_stats: Dict[str, List[str]], **__) -> str:
        node_sch = self.gschema.node_schema
        edge_sch = self.gschema.edge_schema
        node_label = self.gschema.node_neo4j_label
        edge_label = self.gschema.edge_neo4j_label

        MATCH_PART = f"MATCH(n:{node_label})-[e:{edge_label}]-(d:{node_label})"
        RETURN_FIELDS = [
            f"n.{node_sch.id_property.name} as {node_sch.id_property.name}",
            "count(distinct d) as num_neighbours",
            "count(e) as num_edges",
        ]
        if node_sch.properties:
            for prop in node_sch.properties:
                RETURN_FIELDS.append(f"n.{prop.name} as {prop.name}")
        if edge_sch.properties:
            for prop in edge_sch.properties:
                if (prop.type == int) or (prop.type == float):
                    features = self.calculate_numeric_features(f"e.{prop.name}", f"e_{prop.name}")
                    RETURN_FIELDS.extend(features)
                elif prop.type == bool:
                    t_col = (
                        f"sum(CASE WHEN e.{prop.name} = true THEN 1 END) as num_true_e_{prop.name}"
                    )
                    f_col = f"sum(CASE WHEN e.{prop.name} = false THEN 1 END) as num_false_e_{prop.name}"
                    RETURN_FIELDS.append(t_col)
                    RETURN_FIELDS.append(f_col)
                elif prop.type == str:
                    if prop.is_category:
                        for idx, cat in cat_stats[prop.name]:
                            cat_col = f"sum(CASE WHEN e.{prop.name} = '{cat}' THEN 1 END) as num_{idx}_e_{prop.name}"
                            RETURN_FIELDS.append(cat_col)
                else:
                    raise Exception(f"Unknown type - {prop.type}")
        QUERY_ROWS = (
            MATCH_PART,
            f"RETURN {', '.join(RETURN_FIELDS)}",
        )
        return "\n".join(QUERY_ROWS)
