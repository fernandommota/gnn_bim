## Build image
```
docker build --rm -t gnn_bim .
```

## Start Container

``` shell
docker-compose up
```

## Setup Commandas

```
pip install -r requirements.txt
```

## NEO4j Commands

All nodes and relationships.
```
MATCH (n) DETACH DELETE n
```

All indexes and constraints.
```
CALL apoc.schema.assert({},{},true) YIELD label, key RETURN *