from typing import Dict, List

from .base import BaseQueryBuilder


class NeighbourStatsQueryBuilder(BaseQueryBuilder):
    """
    Получаем фичи с соседних узлов:
        - Рассчитываем статистики над числовыми свойствами
        - Счетчики над булевыми и категориальными значениями
    """

    def get_query(self, cat_stats: Dict[str, List[str]], **__) -> str:
        node_sch = self.gschema.node_schema
        node_label = self.gschema.node_neo4j_label
        edge_label = self.gschema.edge_neo4j_label

        MATCH_PART = f"MATCH(n:{node_label})-[e:{edge_label}]-(d:{node_label})"
        WITH_PART = f"WITH n, collect(distinct d) as neigh"
        UNWIND_PART = "UNWIND neigh as nb"
        RETURN_FIELDS = [f"n.{node_sch.id_property.name} as {node_sch.id_property.name}"]
        if node_sch.properties:
            for prop in node_sch.properties:
                if (prop.type == int) or (prop.type == float):
                    features = self.calculate_numeric_features(f"nb.{prop.name}", f"nb_{prop.name}")
                    RETURN_FIELDS.extend(features)
                elif prop.type == bool:
                    t_col = f"sum(CASE WHEN nb.{prop.name} = true THEN 1 END) as num_true_nb_{prop.name}"
                    f_col = f"sum(CASE WHEN nb.{prop.name} = false THEN 1 END) as num_false_nb_{prop.name}"
                    RETURN_FIELDS.append(t_col)
                    RETURN_FIELDS.append(f_col)
                elif prop.type == str:
                    if prop.is_category:
                        same_col = f"sum(CASE WHEN nb.{prop.name} = n.{prop.name} THEN 1 END) as num_same_nb_{prop.name}"
                        RETURN_FIELDS.append(same_col)
                        for idx, cat in cat_stats[prop.name]:
                            cat_col = f"sum(CASE WHEN nb.{prop.name} = '{cat}' THEN 1 END) as num_{idx}_nb_{prop.name}"
                            RETURN_FIELDS.append(cat_col)
                else:
                    raise Exception(f"Unknown type - {prop.type}")
        QUERY_ROWS = (
            MATCH_PART,
            WITH_PART,
            UNWIND_PART,
            f"RETURN {', '.join(RETURN_FIELDS)}",
        )
        return "\n".join(QUERY_ROWS)
