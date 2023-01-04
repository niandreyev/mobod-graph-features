# Построение фичей поверх графовой БД Neo4j

### Структура проекта

- `graphfs` - набор Python-классов, осуществляющих построение датафрейма на основе данных в БД и переданной структуры графа
- `neo4j_db` - папка содержит нужный конфиг и плагин для запуска библиотеки `graph-data-science`, нужна для алгоритмов и эмбеддингов
- `queries` - Папка содержит cypher-скрипты для инициализации БД (очистка + загрузка данных)
- `results` - Папка с результатами применения `graphfs` над графами
- `main.py` - Основной скрипт, запускающий построение фичей 

### Какие фичи строятся?

1. Все фичи связанные с вершиной и ребрами исходящими из нее (node_stats):
    - Столбец id узла
    - Число соседей
    - Число ребер
    - Свойства узла
    - Статистики над числовыми свойствами (min,max,avg,sum,median)
    - Счетчики над булевыми и категориальными значениями
2. Фичи из первого пункта сгруппированные по категориальным переменным (category_stats)
3. Фичи усредненные по соседям
4. Алгоритмы:
    - [Centrality](https://neo4j.com/docs/graph-data-science/current/algorithms/centrality/): PageRank, Betweenness Centrality, Closeness Centrality
    - [Community detection](https://neo4j.com/docs/graph-data-science/current/algorithms/community/): Louvain, Label Propagation, Local Clustering Coefficient
    - [Embeddings](https://neo4j.com/docs/graph-data-science/current/machine-learning/node-embeddings/): Fast Random Projection

### Как запустить?

`docker-compose up`

1. Первым поднимется контейнер с БД - **neo4j**
2. Затем контейнер **init-neo4j** наполнит БД данными о двух графах
3. Запуск в отдельном контейнере скрипта `main.py`