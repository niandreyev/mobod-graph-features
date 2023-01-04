from itertools import chain

from .base import BaseQueryBuilder


class AlgorithmsQueryBuilder(BaseQueryBuilder):

    CENTRALITIES = [
        ("gds.pageRank", "score", "pagerank_score"),
        ("gds.betweenness", "score", "betweenness_score"),
        ("gds.beta.closeness", "score", "closeness_score"),
    ]
    COMMUNITIES = [
        ("gds.louvain", "communityId", "louvain_communityId"),
        ("gds.labelPropagation", "communityId", "label_propagation_community"),
        (
            "gds.localClusteringCoefficient",
            "localClusteringCoefficient",
            "localClusteringCoefficient",
        ),
    ]
    EMBEDDINGS = ["gds.fastRP"]

    def get_query(self, *_, n_dim: int = 10, **__) -> str:
        id_prop = self.gschema.node_schema.id_property.name
        QUERIES = []
        for source_fun, res, alias in chain(self.CENTRALITIES, self.COMMUNITIES):
            Q = (
                f"CALL {source_fun}.stream('{self.gschema.graph_projection_name}')",
                f"YIELD nodeId, {res}",
                f"RETURN gds.util.asNode(nodeId).{id_prop} AS {id_prop}, {res} as {alias}",
            )
            QUERIES.append("\n".join(Q))

        EMBEDDING_Q = (
            f"CALL gds.fastRP.stream('{self.gschema.graph_projection_name}', "
            + "{embeddingDimension: "
            + str(n_dim)
            + "})"
            "YIELD nodeId, embedding",
            f"RETURN gds.util.asNode(nodeId).{id_prop} AS {id_prop}, embedding",
        )
        QUERIES.append("\n".join(EMBEDDING_Q))
        return QUERIES
