import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine, Base
from app.models import models
from app.routers import company, auth, inventory, supplier, purchase_order, production, customs, risk, exchange, oil

app = FastAPI(title="Supply Twin-X API")

cors_origins = [
    origin.strip()
    for origin in os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(company.router)
app.include_router(auth.router)
app.include_router(inventory.router)
app.include_router(supplier.router)
app.include_router(purchase_order.router)
app.include_router(production.router)
app.include_router(customs.router)
app.include_router(risk.router, prefix="/risk", tags=["Risk"])
app.include_router(exchange.router)
app.include_router(oil.router)

@app.get("/")
def root():
    return {"message": "Supply Twin-X API is running"}