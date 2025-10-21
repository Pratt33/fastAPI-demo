from fastapi import FastAPI, Path, HTTPException, Query
import json
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Optional
from fastapi.responses import JSONResponse

app=FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="The ID of the patient", example="P001")]
    name: Annotated[str, Field(..., description="The name of the patient", example="John Doe")]
    age: Annotated[int, Field(..., description="The age of the patient", example=30)]
    height: Annotated[float, Field(..., description="The height of the patient in meters", example=1.75)]
    weight: Annotated[float, Field(..., description="The weight of the patient in kilograms", example=70)]


    @computed_field
    @property
    def bmi(self)-> float:
        return round(self.weight/(self.height**2), 2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 24.9:
            return "Normal weight"
        elif 25 <= self.bmi < 29.9:
            return "Overweight"
        else:
            return "Obesity"


class PatientsUpdate(BaseModel):
    name:Annotated[Optional[str], Field(default=None)]
    city:Annotated[Optional[str], Field(default=None)]
    age:Annotated[Optional[int], Field(default=None)]
    gender:Annotated[Optional[str], Field(default=None)]
    height:Annotated[Optional[float], Field(default=None)]
    weight:Annotated[Optional[float], Field(default=None)]

def read_data():
    with open('patients.json', 'r') as f:
        return json.load(f)
    

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f, indent=4)

@app.get('/')
def hello():
    return {"message": "Patient Management System"}

@app.get('/about')
def about():
    return {"message": "A fully functional API for managing patients."}

@app.get('/view')
def view():
    return read_data()

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str=Path(..., description="The ID of the patient", example="P001")):
    data=read_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get('/sort')
def sort(sort_by: str=Query(..., description="sort by height, weight or bmi"), order: str=Query('asc', description="asc or desc")):
    valid_fields=['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort_by field. Must be one of {valid_fields}")
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail="Invalid order. Must be 'asc' or 'desc'")
    
    data=read_data()

    sort_order=True if order=='desc' else False

    sorted_data=dict(sorted(data.items(), key=lambda item: item[1][sort_by], reverse=sort_order))

    return sorted_data


@app.put('/edit/{patient_id}')
def update_data(patient_id: str, patient_update: PatientsUpdate):

    data=read_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    existing_patient=data[patient_id]
    
    updated_info=patient_update.model_dump(exclude_unset=True) # Get only provided fields in the update request in a dict

    for key, value in updated_info.items():
        existing_patient[key]=value

    # creating id field in existing_patient as it is not present in there which is required to create Patient object
    existing_patient['id']=patient_id # we're not allowing id updates so, ensure it remains the same

    updated_patient_obj=Patient(**existing_patient) # create a Patient object to recalculate bmi and verdict
    updated_patient_info=updated_patient_obj.model_dump() # get all fields as a dict

    data[patient_id]=updated_patient_info # update the patient info in data

    save_data(data) # save the updated data

    return JSONResponse(content={"message": "Patient data updated successfully", "patient": updated_patient_info})


@app.delete('/delete/{patient_id}')
def delete_data(patient_id: str):
    data=read_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(content={"message": "Patient data deleted successfully"})