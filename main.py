from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the MongoDB connection string and secret key from environment variables
MONGODB_URL = os.environ.get("MONGODB_URL")
SECRET_KEY = os.environ.get("SECRET_KEY")

client = MongoClient(MONGODB_URL)
db = client.record  # Replace 'your_database_name' with your actual database name
sales_collection = db.sales  # Adjust 'sales' to your collection name

app = FastAPI()

@app.get("/")
async def root():
    return FileResponse("index.html")

class Product(BaseModel):
    product: str

@app.post("/buy")
async def buy_product(product: Product):
    # Insert sale record into MongoDB
    sale_record = {
        "product": product.product,
        "timestamp": datetime.utcnow()
    }
    sales_collection.insert_one(sale_record)
    return {"message": f"Successfully purchased {product.product}"}

@app.get("/report")
async def sales_report(x_secret_key: str = Header(None)):
    if x_secret_key != SECRET_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # Aggregate sales from MongoDB
    pipeline = [
        {"$group": {
            "_id": "$product",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    sales_report = list(sales_collection.aggregate(pipeline))
    return {"sales_report": sales_report}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
