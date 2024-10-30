from dotenv import load_dotenv

from neo4j import GraphDatabase

from langchain_community.graphs import Neo4jGraph

from ifc_to_graph import convert_ifc_to_graph_document


def create_or_connecto_to_graph(database):

    return Neo4jGraph()

def save_graph(graph, entities):

    graph.add_graph_documents(
        entities,
        baseEntityLabel=True,
        include_source=False
    )

graph_ifc_cost = create_or_connecto_to_graph("ifc_cost")

entities = convert_ifc_to_graph_document('input/ifc_cost/ifc_cost_sample_clean.ifc')

save_graph(graph_ifc_cost, entities)