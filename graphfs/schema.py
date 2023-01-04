from dataclasses import dataclass
from typing import List, Type


@dataclass
class Property:
    """
    Схема, описывающий свойства (одно поле) в графовой БД
        name - Наименование свойства
        type - Тип
    """

    name: str
    type: Type
    is_category: bool = False


@dataclass
class NodeSchema:
    """
    Схема, описывающая ноды в графе
        id_property - уникальное свойство, которое используется в качестве id
        properties - дополнительные свойства нод
    """

    id_property: Property
    properties: List[Property] = None


@dataclass
class EdgeSchema:
    """
    Схема, описывающая ребра в графе
        properties - дополнительные свойства ребер
    """

    properties: List[Property] = None


@dataclass
class GraphSchema:
    """
    Схема, описывающая граф (наименование полей и типы данных)
    В данной реализации наложено доп ограничение на ноды одного типа.
    """

    node_neo4j_label: str
    edge_neo4j_label: str
    graph_projection_name: str
    node_schema: NodeSchema
    edge_schema: EdgeSchema
