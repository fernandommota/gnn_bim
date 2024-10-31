import ifcopenshell
import ifcopenshell.api.cost
import ifcopenshell.api.control

def add_cost_schedule(model, name):
    schedule = ifcopenshell.api.cost.add_cost_schedule(model,name=name)
    
    return schedule

def add_cost_item(model, cost_schedule, attributes):
    cost_item = ifcopenshell.api.cost.add_cost_item(model,cost_schedule=cost_schedule)

    ifcopenshell.api.cost.edit_cost_item(model, cost_item=cost_item, attributes=attributes)

    return cost_item

def add_cost_item_quantity(model, cost_item, ifc_class):
    item_quantity = ifcopenshell.api.cost.add_cost_item_quantity(model, cost_item=cost_item, ifc_class=ifc_class)

def assign_cost_item_quantity(model, cost_item, products, prop_name):
    item_quantity = ifcopenshell.api.cost.assign_cost_item_quantity(model, cost_item=cost_item, products=products, prop_name=prop_name)


def add_cost_value(model, cost_item, attributes):
    cost_value = ifcopenshell.api.cost.add_cost_value(model, parent=cost_item)
    
    ifcopenshell.api.cost.edit_cost_value(model, cost_value=cost_value, attributes=attributes)

    """
        # Option 2: This cost item will have a unit cost of 5.0 per unit
        # area, multiplied by the quantity of area specified explicitly as
        # 3.0, giving us a subtotal cost of 15.0.
        item2 = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=schedule)
        value = ifcopenshell.api.cost.add_cost_value(model, parent=item2)
        ifcopenshell.api.cost.edit_cost_value(model, cost_value=value,
            attributes={"AppliedValue": 5.0})
        quantity = ifcopenshell.api.cost.add_cost_item_quantity(model,
            cost_item=item2, ifc_class="IfcQuantityVolume")
        ifcopenshell.api.cost.edit_cost_item_quantity(model,
            physical_quantity=quantity, "attributes": {"VolumeValue": 3.0})

        # A cost value may also be specified in terms of the sum of its
        # subcomponents. In this case, it's broken down into 2 subvalues.
        item1 = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=schedule)
        value = ifcopenshell.api.cost.add_cost_value(model, parent=item1)
        subvalue1 = ifcopenshell.api.cost.add_cost_value(model, parent=value)
        subvalue2 = ifcopenshell.api.cost.add_cost_value(model, parent=value)

        # This specifies that the value is the sum of all subitems
        # regardless of their cost category. The first subvalue is 2.0 and
        # the second is 3.0, giving a total value of 5.0.
        ifcopenshell.api.cost.edit_cost_value(model, cost_value=value, attributes={"Category": "*"})
        ifcopenshell.api.cost.edit_cost_value(model,
            cost_value=subvalue1, attributes={"AppliedValue": 2.0})
        ifcopenshell.api.cost.edit_cost_value(model,
            cost_value=subvalue2, attributes={"AppliedValue": 3.0})
    pass
    """


def write_graph_as_ifc(data, ifc_source_file_path, ifc_target_file_path):

    model = ifcopenshell.open(ifc_source_file_path)
    cost_schedule = add_cost_schedule(model, "Tabela de Composições por fe.maia (+10%)")
    quantityFlag=False
    ifc_cost_item = {}
    for entity in data:
        type = entity["type"]
        if type == "IfcCostItem":
            cost_items = entity["response"]
            for cost_item in cost_items:
                attributes=cost_item["attributes"]
                ifc_cost_item[cost_item["id"]] = add_cost_item(model, cost_schedule, attributes) 

                prop_names = {
                    "IfcWall": "NetSideArea",
                    "IfcCovering": "GrossArea",
                    "IfcDoor": "IfcQuantityCount"
                }
                for assignment in cost_item["assignments"]:
                    products = model.by_type(assignment["type"])
                    if prop_names[assignment["type"]] == "IfcQuantityCount" and quantityFlag==False:
                        # special for one unit per element
                        for product in products:
                            ifcopenshell.api.control.assign_control(model, relating_control=ifc_cost_item[cost_item["id"]],related_object=product)
                        # special for one unit per element
                        add_cost_item_quantity(model, ifc_cost_item[cost_item["id"]], "IfcQuantityCount")
                        quantityFlag = True
                    else:
                        assign_cost_item_quantity(model, ifc_cost_item[cost_item["id"]], products, prop_names[assignment["type"]])
        elif type == "IfcCostItemValue" :
            cost_values = entity["response"]
            for cost_value in cost_values:
                attributes = cost_value["attributes"]
                if attributes.get("AppliedValue") is not None:
                    attributes["AppliedValue"] = float(attributes["AppliedValue"]) * 1.10
                relationship = cost_value["relationship"]
                cost_item = ifc_cost_item[relationship["id"]]
                add_cost_value(model, cost_item, attributes)    

    model.write(ifc_target_file_path)