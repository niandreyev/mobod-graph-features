from graphfs.connector import DBConnector
from graphfs.data_builder import DataBuilder
from graphfs.schema import EdgeSchema, GraphSchema, NodeSchema, Property
import os



if __name__ == "__main__":
    LOGIN = os.environ["NEO4J_LOGIN"]
    PASSWORD = os.environ["NEO4J_PASSWORD"]
    conn = DBConnector("neo4j", "7687", LOGIN, PASSWORD)

    roads_schema = GraphSchema(
        "City",
        "EROAD",
        "City_project",
        NodeSchema(Property("name", str), [Property("country_code", str, True)]),
        EdgeSchema(
            [Property("distance", int), Property("number", str), Property("watercrossing", bool)]
        ),
    )
    roads_build = DataBuilder(conn, roads_schema)
    roads_res = roads_build.get_features()
    roads_res.to_csv("results/roads.csv", index=None)

    people_schema = GraphSchema(
        "Person",
        "KNOWS",
        "People_project",
        NodeSchema(Property("name", str), [Property("age", int)]),
        EdgeSchema([Property("weight", float)]),
    )
    people_build = DataBuilder(conn, people_schema)
    people_res = people_build.get_features()
    people_res.to_csv("results/people.csv", index=None)
