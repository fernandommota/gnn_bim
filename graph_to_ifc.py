import ifcopenshell
import ifcopenshell.api.cost

def add_cost_schedule(model, name):
    schedule = ifcopenshell.api.cost.add_cost_schedule(model,name=name)
    
    return schedule

def add_cost_item(model, cost_schedule):
    cost_item = ifcopenshell.api.cost.add_cost_item(model,cost_schedule=cost_schedule)

    ifcopenshell.api.cost.edit_cost_item(model, cost_item=cost_item, attributes={
        "Name": "cost_item Sample",
    })
    
    cost_value = ifcopenshell.api.cost.add_cost_value(model, parent=cost_item)
    
    ifcopenshell.api.cost.edit_cost_value(model, cost_value=cost_value, attributes={
        "Name": "cost_value Sample",
        "AppliedValue": 42.0
    })

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


ifc_input_file_path = "input/ifc_cost/ifc_cost_sample_clean.ifc"
model = ifcopenshell.open(ifc_input_file_path)
cost_schedule = add_cost_schedule(model, "Tabela de Composições por fe.maia")
add_cost_item(model, cost_schedule)

ifc_output_file_path = "output/ifc_cost/ifc_cost_sample_custom.ifc"
model.write(ifc_output_file_path)