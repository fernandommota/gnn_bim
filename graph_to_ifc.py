import ifcopenshell

import ifcopenshell.api

def add_cost_schedule(model, attributes):
    schedule = ifcopenshell.api.run("cost.add_cost_schedule",model)
    ifcopenshell.api.run("cost.edit_cost_schedule", model, cost_schedule=schedule,attributes=attributes)
    
    return model

def add_ifc_cost_item(model):
    
    pass


ifc_input_file_path = "input/ifc_cost/ifc_cost_sample_clean.ifc"
cost_schedule_attributes = {
    "Name": "Tabela de Composições por fe.maia"
}
model = ifcopenshell.open(ifc_input_file_path)
add_cost_schedule(model, cost_schedule_attributes)

ifc_output_file_path = "output/ifc_cost/ifc_cost_sample_custom.ifc"
model.write(ifc_output_file_path)