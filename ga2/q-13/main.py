import csv
from fastapi import FastAPI,Query
from typing import List, Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"]) # Allow GET requests from all origins

# remeber if fastapi is insatlled in the uv environmet only ,as  it requires uvicorn too so use uv and uvicorn to run fastapi apps
#read csv data from q-fastapi.csv and store in memory,as a list of dicts
data = []
with open('q-fastapi.csv', mode='r') as file:
    csv_reader = csv.DictReader(file)   # it will be a n object that will iterate over lines of the csv file, each row will be a dict with key as column name and value as cell value  {'studentId': '1980', 'class': '9F'}
    print(csv_reader.fieldnames) 
    for row in csv_reader: # each row is a dict {'studentId': '1980', 'class': '9F'}
        data.append(
            {
                "studentId": int(row['studentId']), # convert to int, coz qstn requires int
                "class": row['class']
            }   
        )

#QUERY PARAMS
@app.get("/api")
#Because FastAPI will NEVER magically turn Optional[str] into a list.
def get_students_or_by_class(class_list: Optional[List[str]] = Query(default=None, alias="class")):  # class_list is a list of strings or None if not provided
    # the above line means class_list is an optional query param, which can have multiple values like ?class=9F&class=10A etc, and will be passed as a list of strings to the function, 
    # Query is used to specify that its a query param, default=None means its optional, alias="class" is used to map the query param name "class" to the function parameter name class_list (because class is a reserved keyword in python so we use class_list instead)
    print(f"class_list param value: {class_list}")
    if class_list is not None:
                filtered_data = [student for student in data if student["class"] in class_list]
                return {"students": filtered_data}
    return {"students": data}

import uvicorn

if __name__ == "__main__":
    uvicorn.run(app,port=8004)
