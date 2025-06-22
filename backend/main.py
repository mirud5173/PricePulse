from fastapi import FastAPI
from fastapi import Query
from urllib.parse import quote
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import models
import database
from routers import users, products, prices, scrape, alerts
from scheduler import scheduler
from dotenv import load_dotenv
from fastapi.responses import FileResponse

load_dotenv()
app = FastAPI()

@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_path, "login.html"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

models.Base.metadata.create_all(bind=database.engine)

# Include routers
app.include_router(users.router)
app.include_router(products.router)
app.include_router(prices.router)
app.include_router(scrape.router)
app.include_router(alerts.router)

# ✅ Start the scheduler on startup
@app.on_event("startup")
def start_scheduler():
    scheduler.start()

# Serve frontend
import os
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
app.mount("/static", StaticFiles(directory=frontend_path), name="static")
