from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class DeliveryTimeRequest(BaseModel):
    seller_zip_code_prefix: int
    customer_zip_code_prefix: int
    delivery_distance_km: int

class DeliveryTimeResponse(BaseModel):
    seller_zip_code_prefix: int
    customer_zip_code_prefix: int
    delivery_distance_km: int
    delivery_time: float

@app.post("/delivery_time", response_model=DeliveryTimeResponse)
async def delivery_time(request: DeliveryTimeRequest):
    try:
        seller_zip_code_prefix = request.seller_zip_code_prefix
        customer_zip_code_prefix = request.customer_zip_code_prefix
        delivery_distance_km = request.delivery_distance_km

        delivery_time = delivery_distance_km * 1.2  # Example logic

        # Return the result as JSON
        return DeliveryTimeResponse(
            seller_zip_code_prefix=seller_zip_code_prefix,
            customer_zip_code_prefix=customer_zip_code_prefix,
            delivery_distance_km=delivery_distance_km,
            delivery_time=delivery_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
