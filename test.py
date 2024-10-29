from dotenv import load_dotenv

from ifc_to_graph import convert_ifc_to_graph_document


graph_ifc = convert_ifc_to_graph_document('input/ifc_cost/ifc_cost_sample.ifc')
