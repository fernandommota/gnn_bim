import os

import json


from dotenv import load_dotenv

from neo4j import GraphDatabase

from langchain_community.graphs import Neo4jGraph

from ifc_to_graph import convert_ifc_to_graph_document

from graph_to_ifc import write_graph_as_ifc


def create_or_connecto_to_graph(database):

    return Neo4jGraph()

def save_graph(graph, entities):

    graph.add_graph_documents(
        entities,
        baseEntityLabel=True,
        include_source=False
    )

    driver = GraphDatabase.driver(
        uri = os.environ["NEO4J_URI"],
        auth = (
            os.environ["NEO4J_USERNAME"],
            os.environ["NEO4J_PASSWORD"]
        )
    )

    def create_fulltext_index(tx):
        query = '''
        CREATE FULLTEXT INDEX `fulltext_entity` 
        FOR (n:__Entity__) 
        ON EACH [n.type];
        '''
        tx.run(query)

    ## Function to execute the query
    def create_index():
        with driver.session() as session:
            session.execute_write(create_fulltext_index)
            print("Fulltext index created successfully.")

    # Call the function to create the index
    try:
        create_index()
    except:
        pass

    # Close the driver connection
    driver.close()

    return graph

def convert_string_to_dictionary(result):
    response_dict = []
    for item in result:
        if item is not None:
            response_dict.append(json.loads(item))

    return response_dict

def graph_retriever(graph, entities):

    """
    Collects the neighborhood of entities mentioned
    in the question
    """
    results = []
    for entity in entities:
        result = []
        entity_type = entity["type"]
        if entity_type == "IfcWall":
            response = graph.query(
                """CALL db.index.fulltext.queryNodes('fulltext_entity', $query, {limit:200})
                YIELD node,score
                CALL {
                WITH node
                MATCH (node)<-[r:IFC]-(neighbor)
                RETURN '{"id":"'+node.id + '", "type":"' + node.type + '", "attributes": { "Qto_WallBaseQuantitiesGrossSideArea":"' + node.Qto_WallBaseQuantitiesGrossSideArea + '"}}' AS output
                }
                RETURN output LIMIT 50
                """,
                {"query": entity["type"]},
            )
            #[print(el['output']) for el in response]
            temp = [el['output'] for el in response]
            result = list(dict.fromkeys(temp))
            response_dict = {}
        elif entity_type == "IfcCovering":
            response = graph.query(
                """CALL db.index.fulltext.queryNodes('fulltext_entity', $query, {limit:200})
                YIELD node,score
                CALL {
                WITH node
                MATCH (node)<-[r:IFC]-(neighbor)
                RETURN '{"id":"'+node.id + '", "type":"' + node.type + '", "attributes": { "Qto_CoveringBaseQuantitiesGrossArea":"' + node.Qto_CoveringBaseQuantitiesGrossArea + '"}}' AS output
                }
                RETURN output LIMIT 50
                """,
                {"query": entity["type"]},
            )
            #[print(el['output']) for el in response]
            temp = [el['output'] for el in response]
            result = list(dict.fromkeys(temp))
            response_dict = {}
        elif entity_type == "IfcDoor":
            response = graph.query(
                """CALL db.index.fulltext.queryNodes('fulltext_entity', $query, {limit:200})
                YIELD node,score
                CALL {
                WITH node
                MATCH (node)<-[r:IFC]-(neighbor)
                RETURN '{"id":"'+node.id + '", "type":"' + node.type + '"}' AS output
                }
                RETURN output LIMIT 50
                """,
                {"query": entity["type"]},
            )
            #[print(el['output']) for el in response]
            temp = [el['output'] for el in response]
            result = list(dict.fromkeys(temp))
            response_dict = {}
        elif entity_type == "IfcCostItem":
            response = graph.query(
                """CALL db.index.fulltext.queryNodes('fulltext_entity', $query, {limit:200})
                YIELD node,score
                CALL {
                WITH node 
                MATCH (n:IfcCostItem)
                RETURN '{"id":"'+node.id + '", "type":"' + node.type + '", "attributes":{ "Name":"' + node.name + '"}}' AS output
                }
                RETURN output LIMIT 2000
                """,
                {"query": entity["type"]},
            )
            temp = [el['output'] for el in response]
            result = list(dict.fromkeys(temp))

            response_dict = convert_string_to_dictionary(result)

            response = graph.query(
                """CALL db.index.fulltext.queryNodes('fulltext_entity', $query, {limit:200})
                YIELD node,score
                CALL {
                WITH node
                MATCH (node)<-[r:IFCRELCOST]-(neighbor)
                RETURN '{"id":"'+node.id + '", "assignment":{ "id":"' + neighbor.id + '", "type":"' + neighbor.type + '"}}' AS output
                }
                RETURN output LIMIT 2000
                """,
                {"query": entity["type"]},
            )
            assignments = convert_string_to_dictionary([el['output'] for el in response])

            for item in response_dict:
                id = item["id"]
                item["assignments"] = []
                for assignment in assignments:
                    if assignment["id"] == id:
                        item["assignments"].append(assignment["assignment"]) 

        elif entity_type == "IfcCostItemValue":
            response = graph.query(
                """CALL db.index.fulltext.queryNodes('fulltext_entity', $query, {limit:200})
                YIELD node,score
                CALL {
                WITH node
                MATCH (node)<-[r:IFCRELCOSTITEMVALUE]-(neighbor)
                RETURN '{"id":"'+node.id + '", "type":"' + node.type + '", "attributes":{ "Name":"' + node.name + '","AppliedValue":"' + node.value + '"},"relationship": {"type": "' + type(r) +'", "id": "' + neighbor.id + '"}}' AS output
                }
                RETURN output LIMIT 2000
                """,
                {"query": entity["type"]},
            )
            result = [el['output'] for el in response]

            response_dict = convert_string_to_dictionary(result)

        results.append({
            "type": entity_type,
            "response": response_dict
        })


    return results

graph_ifc_cost = create_or_connecto_to_graph("ifc_cost")

entities = convert_ifc_to_graph_document('input/ifc_cost/ifc_cost_sample.ifc')

graph = save_graph(graph_ifc_cost, entities)

entities = [
    {"type":"IfcWall"},
    {"type":"IfcCovering"},
    {"type":"IfcDoor"},
    {"type":"IfcCostItem"},
    {"type":"IfcCostItemValue"},
]
results = graph_retriever(graph, entities)

ifc_source_file_path = "input/ifc_cost/ifc_cost_sample_clean.ifc"
ifc_target_file_path = "output/ifc_cost/ifc_cost_sample_custom.ifc"
write_graph_as_ifc(results, ifc_source_file_path, ifc_target_file_path)