from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine, Base
from app.models import models
from app.routers import company, auth, inventory, supplier, purchase_order, production, customs

app = FastAPI(title="Supply Twin-X API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
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

@app.get("/")
def root():
    return {"message": "Supply Twin-X API is running"}