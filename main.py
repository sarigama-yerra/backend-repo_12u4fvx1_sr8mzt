import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Project, Testimonial, Client, Message

app = FastAPI(title="Branding & Animation Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helpers
class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        try:
            return str(ObjectId(v))
        except Exception:
            raise ValueError("Invalid ObjectId")


def serialize_doc(doc: dict):
    if not doc:
        return doc
    doc["id"] = str(doc.get("_id"))
    doc.pop("_id", None)
    return doc


@app.get("/")
def read_root():
    return {"message": "Studio API running"}


# ---------- Projects (Portfolio) ----------
@app.post("/api/projects")
def create_project(project: Project):
    try:
        new_id = create_document("project", project)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects")
def list_projects(category: Optional[str] = None, featured: Optional[bool] = None, limit: int = 100):
    filt = {}
    if category:
        filt["category"] = category
    if featured is not None:
        filt["featured"] = featured
    try:
        docs = get_documents("project", filt, limit)
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Testimonials ----------
@app.post("/api/testimonials")
def create_testimonial(t: Testimonial):
    try:
        new_id = create_document("testimonial", t)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/testimonials")
def list_testimonials(limit: int = 50):
    try:
        docs = get_documents("testimonial", {}, limit)
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Clients ----------
@app.post("/api/clients")
def create_client(c: Client):
    try:
        new_id = create_document("client", c)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/clients")
def list_clients(limit: int = 100):
    try:
        docs = get_documents("client", {}, limit)
        return [serialize_doc(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Contact Messages ----------
@app.post("/api/messages")
def submit_message(m: Message):
    try:
        new_id = create_document("message", m)
        return {"id": new_id, "status": "received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
