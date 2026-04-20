from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
import numpy as np

app = FastAPI()
#cd vercel-ga8-q3/api
#uvicorn main:app --reload --host 127.0.0.1 --port 8000

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Train model at startup
iris = load_iris()
model = DecisionTreeClassifier(random_state=42)
model.fit(iris.data, iris.target)
class_names = ["setosa", "versicolor", "virginica"]

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/predict")
async def predict(sl: float, sw: float, pl: float, pw: float):
    features = np.array([[sl, sw, pl, pw]])
    pred = int(model.predict(features)[0])
    return {"prediction": pred, "class_name": class_names[pred]}