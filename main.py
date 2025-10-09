from fastapi import FastAPI, Path, HTTPException, Query
import json

app=FastAPI()

def read_data():
    with open('patients.json', 'r') as f:
        return json.load(f)

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