from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import numpy as np
#add numpy in reqs.txt for vercel 

#to run locally: uvicorn api.main:app --reload  (reload for auto restart on code changes) i have pip installed fastapi and uvicorn
#then check in another terminal by: curl -X POST http://127.0.0.1:8000/api/latency   -H "Content-Type: application/json"   -d '{"regions":["amer"],"threshold_ms":157}'


#after locally testing output
# run
# vercel (preview env)  or vercel --prod( prod env)
#make sure vercel is installed follow notes tds-entrance q-25

app = FastAPI()
# Middleware for simple cases

# Middleware handles most requests automatically
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all websites
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
    expose_headers=["*"] # expose all headers ie allow client side JS to access them
)


#VIDEO DEMO PURPOSES ONLY
#root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI application!"}


#NO NEEEEEEED
# OPTIONS route for preflight requests to /api/latency
# without this i dot error in dev tools
#Access to fetch at 'https://vercel-fastapi-9j8pk1el3-theerthas-projects-db32a08a.vercel.app/api/latency' from origin 'https://exam.sanand.workers.dev' has been blocked by CORS policy
# : Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource.

# @app.options("/api/latency")
# async def preflight_latency(request: Request):
#     return JSONResponse(
#         content={"message": "OK"},
#         headers={
#             "Access-Control-Allow-Origin": "*",
#             "Access-Control-Allow-Methods": "POST, OPTIONS, GET",
#             "Access-Control-Allow-Headers": "Content-Type, Authorization",
#             "Access-Control-Expose-Headers": "Access-Control-Allow-Origin"   
#         },
#     )




#qstn 26 ans
class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: int

#data=[]

def load_json_data():
    #global data

    # Function to load JSON data
    #os.path.dirname(__file__) gives the directory of the current file, os.path.join is used to construct the path to the json file
    #so here we are constructing the path to the json file which is in the parent directory(api) of the current file
    file_path=os.path.join(os.path.dirname(__file__), '..', 'q-vercel-latency.json')
    with open(file_path, 'r') as f:
        #below json.load(f) loads the json data from the file and returns it as a python list of dictionaries (as the json file contains an array of objects)
        
        #data=json.load(f)
        return json.load(f)
    
        


#post method to api/latency endpoint
@app.post("/api/latency")
def per_region_metrics(request: RequestBody):
    #global data 
    try:
        #post has a request body
        #the params in the above api function are taken from the request body automatically by FastAPI if they are of type Pydantic model, so here student param is taken from request body,student-id is taken from path(its a path param)
        # so "request" param will have the data sent in the request body as json
        #if data is global , then no need of this line
        data = load_json_data()
        result={}
        result["regions"] = {}
        for region in request.regions:
            region_data = [entry for entry in data if entry["region"] == region]
            latencies = [entry["latency_ms"] for entry in region_data]
            uptimes= [entry["uptime_pct"] for entry in region_data]

            avg_latency = np.mean(latencies)

            p95_latency = np.percentile(latencies, 95)
            avg_uptime = np.mean(uptimes)
            breaches= sum(1 for latency in latencies if latency > request.threshold_ms)

            result["regions"][region] = {
                "average_latency": avg_latency,
                "p95_latency": p95_latency,
                "avg_uptime": avg_uptime,
                "breaches": breaches
            }

        return result
    except Exception as e:
        return {"error": str(e)}

# if __name__ == "__main__":
#     print("Initializing with (FastAPI)...")
#     uvicorn.run(app,port=8001)

#actually we can declare data=[] as gloabal variable and load the json data in it at the start of the app, 
# @app.on_event("startup")
# async def startup_event():
#     data = load_json_data()

#ie data = load_json_data() at the start of the app, and then use this data variable in the per_region_metrics function,
#declare "global data" in the per_region_metrics function and use it, this way we will load the json data only once at the start of the app and store it in memory,
# so that we dont have to load the json data from file every time the endpoint is hit, 
# which will improve performance as file I/O is slow,
#  but for simplicity we are loading the json data from file every time the endpoint is hit, which is fine for this use case as the json file is small and we are not expecting high traffic. But in a real world scenario with large json files and high traffic, we should load the json data once at the start of the app and store it in a global variable or in memory cache like Redis or Memcached.


#vercel.json is a vercel configuration file for deploying a FastAPI application.
#It specifies the build and routing settings needed for Vercel to properly serve the FastAPI app.
# The file should be placed in the root directory of your project.
# builds: This section defines how to build the application.
# The src/api/main.py file is specified as the entry point for the FastAPI application.
# routes: This section defines the routing rules for incoming requests.
# All requests to the root path (/) are routed to the FastAPI application defined in srcnpm install -g vercelnpm install -g vercel