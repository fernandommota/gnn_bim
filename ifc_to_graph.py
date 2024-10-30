import ifcopenshell
import ifcopenshell.util.cost
import ifcopenshell.util.element

from langchain_core.documents import Document
from langchain_community.graphs.graph_document import GraphDocument, Node, Relationship

from typing import List

def convert_ifc_to_graph_document(ifc_file_path) -> List[GraphDocument]:
    model = ifcopenshell.open(ifc_file_path)

    nodes = []
    relationships = []
    ifc_objects={}
    for ifc_object in model.by_type("IfcObject"):
        if ifc_object.is_a("IfcVirtualElement"):
            continue

        type = ifcopenshell.util.element.get_type(ifc_object)
        psets = {}
        qsets = {}
        if type is not None:
            psets = ifcopenshell.util.element.get_psets(ifc_object, psets_only=True)
            qsets = ifcopenshell.util.element.get_psets(ifc_object, qtos_only=True)

        ifc_objects[ifc_object.id()] = {
            "id": f'#{str(ifc_object.id())}',
            "type":ifc_object.is_a()
        }

        ifc_object_properties={
            "type":ifc_objects[ifc_object.id()]["type"],
            "name": ifc_object.Name,
        }

        if qsets.get("Qto_CoveringBaseQuantities") is not None:
            for item in qsets["Qto_CoveringBaseQuantities"]:
                ifc_object_properties[f'Qto_CoveringBaseQuantities{item}'] = qsets["Qto_CoveringBaseQuantities"][item]

        if qsets.get("Qto_WallBaseQuantities") is not None:
            for item in qsets["Qto_WallBaseQuantities"]:
                ifc_object_properties[f'Qto_WallBaseQuantities{item}'] = qsets["Qto_WallBaseQuantities"][item]
        
        # https://docs.ifcopenshell.org/autoapi/ifcopenshell/util/cost/index.html
        if ifc_objects[ifc_object.id()]["type"] == 'IfcCostItem':

            total_quantities = ifcopenshell.util.cost.get_total_quantity(ifc_object)
            if total_quantities is not None:
                print(ifc_object.id(), ifc_object.Name)

                print('\nquantities')
                print(total_quantities)
                ifc_object_properties[f'CostItemQuantity'] = total_quantities
                ifc_object_properties[f'CostItemTotal'] = 0
                
                cost_values = ifcopenshell.util.cost.get_cost_values(ifc_object)
                for cost_value in cost_values:
                    print('cost_value', cost_value)
                    ifc_objects[cost_value["id"]] = {
                        "id": f'#{str(cost_value["id"])}',
                        "type": 'IfcCostItemValue'
                    }
                    properties={
                        "type":'IfcCostItemValue',
                        "label": cost_value["label"],
                        "name": cost_value["name"],
                        "category": cost_value["category"],
                        "value": cost_value["applied_value"]
                    }
                    
                    nodes.append(
                        Node(
                            id=ifc_objects[cost_value["id"]]["id"],
                            type=ifc_objects[cost_value["id"]]["type"],
                            properties=properties
                        )
                    )

                    source_node = Node(
                        id=ifc_objects[ifc_object.id()]["id"],
                        type=ifc_objects[ifc_object.id()]["type"],
                    )
                    target_node = Node(
                        id=ifc_objects[cost_value["id"]]["id"],
                        type=ifc_objects[cost_value["id"]]["type"],
                    )
                    relationships.append(
                        Relationship(
                            source=source_node,
                            target=target_node,
                            type='IfcRelCostItemValue',
                            properties={},
                        )
                    )

                print('\nassignments')
                cost_assignments = ifcopenshell.util.cost.get_cost_item_assignments(ifc_object)
                for element_assignment in cost_assignments:
                    print(element_assignment.id(), element_assignment.Name, element_assignment.is_a())

                    psets = ifcopenshell.util.element.get_psets(element_assignment, psets_only=True)
                    qsets = ifcopenshell.util.element.get_psets(element_assignment, qtos_only=True)
                    
                    print('\nassignments psets',psets)
                    print('\nassignments psets',qsets)

                    relationship_properties = {
                        "CostItemTotal": 0
                    }
                    for cost_value in cost_values:
                        if element_assignment.is_a() == "IfcCovering":
                            total = qsets["Qto_CoveringBaseQuantities"]["GrossArea"] * cost_value["applied_value"]
                            relationship_properties["CostItemTotal"] += total
                        elif element_assignment.is_a() == "IfcWall":
                            total = qsets["Qto_WallBaseQuantities"]["NetSideArea"] * cost_value["applied_value"]
                            relationship_properties["CostItemTotal"] += total
                        elif element_assignment.is_a() == "IfcDoor":
                            total = 1 * cost_value["applied_value"]
                            relationship_properties["CostItemTotal"] += total

                    source_node = Node(
                        id = f'#{str(element_assignment.id())}',
                        type = element_assignment.is_a(),
                    )
                    target_node = Node(
                        id=ifc_objects[ifc_object.id()]["id"],
                        type=ifc_objects[ifc_object.id()]["type"],
                    )
                    
                    print('\relationship_properties',relationship_properties)
                    ifc_object_properties['CostItemTotal'] += relationship_properties["CostItemTotal"]
                    relationships.append(
                        Relationship(
                            source=source_node,
                            target=target_node,
                            type='IfcRelCost',
                            properties=relationship_properties,
                        )
                    )

                
                print('\n\n')

        nodes.append(
            Node(
                id=ifc_objects[ifc_object.id()]["id"],
                type=ifc_objects[ifc_object.id()]["type"],
                properties=ifc_object_properties
            )
        )

    for ifc_rel in model.by_type("IfcRelationship"):

        relating_object = None
        related_objects = []

        if ifc_rel.is_a("IfcRelAggregates"):
            relating_object = ifc_rel.RelatingObject
            related_objects = ifc_rel.RelatedObjects
        elif ifc_rel.is_a("IfcRelNests"):
            relating_object = ifc_rel.RelatingObject
            related_objects = ifc_rel.RelatedObjects
        elif ifc_rel.is_a("IfcRelAssignsToGroup"):
            relating_object = ifc_rel.RelatingGroup
            related_objects = ifc_rel.RelatedObjects
        elif ifc_rel.is_a("IfcRelConnectsElements"):
            relating_object = ifc_rel.RelatingElement
            related_objects = [ifc_rel.RelatedElement]
        elif ifc_rel.is_a("IfcRelConnectsStructuralMember"):
            relating_object = ifc_rel.RelatingStructuralMember
            related_objects = [ifc_rel.RelatedStructuralConnection]
        elif ifc_rel.is_a("IfcRelContainedInSpatialStructure"):
            relating_object = ifc_rel.RelatingStructure
            related_objects = ifc_rel.RelatedElements
        elif ifc_rel.is_a("IfcRelFillsElement"):
            relating_object = ifc_rel.RelatingOpeningElement
            related_objects = [ifc_rel.RelatedBuildingElement]
        elif ifc_rel.is_a("IfcRelVoidsElement"):
            relating_object = ifc_rel.RelatingBuildingElement
            related_objects = [ifc_rel.RelatedOpeningElement]
        elif ifc_rel.is_a("IfcRelSpaceBoundary"):
            relating_object = ifc_rel.RelatingSpace
            related_objects = [ifc_rel.RelatedBuildingElement]
        else:
            continue

        for related_object in related_objects:
            if related_objects is not None and relating_object is not None and related_object is not None:
                if relating_object.id() in ifc_objects and related_object.id() in ifc_objects:
                    source_node = Node(
                        id=ifc_objects[relating_object.id()]["id"],
                        type=ifc_objects[relating_object.id()]["type"],
                    )
                    target_node = Node(
                        id=ifc_objects[related_object.id()]["id"],
                        type=ifc_objects[related_object.id()]["type"],
                    )
                    relationships.append(
                        Relationship(
                            source=source_node,
                            target=target_node,
                            type=ifc_rel.is_a(),
                            properties={},
                        )
                    )
                    relationships.append(
                        Relationship(
                            source=source_node,
                            target=target_node,
                            type='IFC',
                            properties={},
                        )
                    )

    #print(nodes) 
    #print(relationships) 

    return [GraphDocument(nodes=nodes, relationships=relationships, source=Document(ifc_file_path))]