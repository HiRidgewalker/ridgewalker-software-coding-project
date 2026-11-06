from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Jenkins Demo API")

# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ITEMS = [
    {"id": 1, "name": "Learn Docker"},
    {"id": 2, "name": "Learn Jenkins"},
    {"id": 3, "name": "Learn CI/CD"},
]


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/items")
def get_items():
    return ITEMS


@app.get("/api/items/{item_id}")
def get_item(item_id: int):
    for item in ITEMS:
        if item["id"] == item_id:
            return item
    return {"error": "not found"}