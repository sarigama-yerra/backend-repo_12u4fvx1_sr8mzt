import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId
import requests

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
        # Optional notification
        try:
            webhook = os.getenv("EMAIL_WEBHOOK_URL")
            if webhook:
                payload = {
                    "type": "new_message",
                    "name": m.name,
                    "email": m.email,
                    "company": m.company,
                    "message": m.message,
                    "message_id": new_id,
                }
                requests.post(webhook, json=payload, timeout=5)
        except Exception:
            # Best-effort: ignore notification errors
            pass
        return {"id": new_id, "status": "received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- Seed Demo Content (Protected) ----------
@app.post("/api/seed")
def seed_demo_content(x_admin_token: Optional[str] = Header(default=None, alias="X-Admin-Token")):
    admin_token = os.getenv("ADMIN_TOKEN")
    if not admin_token or x_admin_token != admin_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # Insert sample projects
        sample_projects = [
            {
                "title": "NOVA — Modular Branding Kit",
                "category": "Branding",
                "description": "A restrained visual system with flexible type scales and a mono grid.",
                "image_url": "https://images.unsplash.com/photo-1512295767273-ac109ac3acfa?q=80&w=1600&auto=format&fit=crop",
                "tags": ["Identity", "Guidelines"],
                "featured": True,
                "order": 1
            },
            {
                "title": "Eclipse OS — Motion Language",
                "category": "Motion",
                "description": "A responsive motion spec for product UI and launch content.",
                "image_url": "https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?q=80&w=1600&auto=format&fit=crop",
                "tags": ["UI", "Spec"],
                "featured": True,
                "order": 2
            },
            {
                "title": "Orbit — 3D Brand Toolkit",
                "category": "3D",
                "description": "Procedural materials and light rigs for consistent content at scale.",
                "image_url": "https://images.unsplash.com/photo-1495567720989-cebdbdd97913?q=80&w=1600&auto=format&fit=crop",
                "tags": ["Lookdev", "Toolkit"],
                "featured": False,
                "order": 3
            },
            {
                "title": "Pico — Character Animation Pack",
                "category": "Animation",
                "description": "A library of expressive micro-animations for onboarding and support.",
                "image_url": "https://images.unsplash.com/photo-1545239351-1141bd82e8a6?q=80&w=1600&auto=format&fit=crop",
                "tags": ["Rigging", "2D"],
                "featured": False,
                "order": 4
            }
        ]
        for p in sample_projects:
            try:
                create_document("project", Project(**p))
            except Exception:
                pass

        # Insert sample testimonials
        sample_testimonials = [
            {
                "name": "Alex Kim",
                "role": "Head of Brand",
                "company": "Vector",
                "quote": "They distilled our messy vision into a simple system we use every day."
            },
            {
                "name": "Riya Patel",
                "role": "Product Design Lead",
                "company": "Sona",
                "quote": "Crisp motion work that elevated the whole product."
            }
        ]
        for t in sample_testimonials:
            try:
                create_document("testimonial", Testimonial(**t))
            except Exception:
                pass

        # Insert sample clients
        sample_clients = [
            {"name": "Linear", "website": "https://linear.app", "logo_url": "https://avatars.githubusercontent.com/u/56582216?s=200&v=4"},
            {"name": "Vercel", "website": "https://vercel.com", "logo_url": "https://assets.vercel.com/image/upload/q_auto/front/favicon/vercel/57x57.png"},
            {"name": "Raycast", "website": "https://raycast.com", "logo_url": "https://avatars.githubusercontent.com/u/57921518?s=200&v=4"}
        ]
        for c in sample_clients:
            try:
                create_document("client", Client(**c))
            except Exception:
                pass

        return {"status": "ok"}
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
