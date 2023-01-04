import pandas as pd

from .connector import DBConnector
from .query_builders import (
    AlgorithmsQueryBuilder,
    BaseQueryBuilder,
    CategoryStatsQueryBuilder,
    NeighbourStatsQueryBuilder,
    NodesStatsQueryBuilder,
)
from .schema import GraphSchema


class DataBuilder:
    def __init__(self, db_conn: DBConnector, graph_schema: GraphSchema) -> None:
        self.db_conn = db_conn
        self.graph_schema = graph_schema

    def _build_cat_feat(self):
        """Сбор всех возможных значений у категориальных фичей"""
        queries = BaseQueryBuilder(self.graph_schema).get_cat_stats_query()
        cat_feat = {}
        for prop_name, q in queries:
            query_res = self.db_conn.get_query_result(q)
            cat_feat[prop_name] = [(idx, r) for idx, r in enumerate(query_res.iloc[:, 0].to_list())]
        return cat_feat

    def _get_df(self, builder_class, cat_stats):
        query = builder_class(self.graph_schema).get_query(cat_stats)
        if query is None:
            return None
        if isinstance(query, list):
            return [self.db_conn.get_query_result(q) for q in query]
        return self.db_conn.get_query_result(query)

    def get_features(self):
        main_col = self.graph_schema.node_schema.id_property.name
        cat_feat = self._build_cat_feat()
        base_df = self._get_df(NodesStatsQueryBuilder, cat_feat)
        neigh_df = self._get_df(NeighbourStatsQueryBuilder, cat_feat)
        cat_dfs = self._get_df(CategoryStatsQueryBuilder, cat_feat)
        alg_dfs = self._get_df(AlgorithmsQueryBuilder, cat_feat)

        mega_df = pd.merge(base_df, neigh_df, on=main_col)
        if cat_dfs:
            for c_df in cat_dfs:
                mega_df = pd.merge(mega_df, c_df, on=c_df.columns[0])

        for a_df in alg_dfs:
            mega_df = pd.merge(mega_df, a_df, on=main_col)

        return mega_df
