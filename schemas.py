"""
Database Schemas for Branding & Animation Studio

Each Pydantic model corresponds to a MongoDB collection.
Collection name is the lowercase of the class name.

Examples:
- Project -> "project"
- Testimonial -> "testimonial"
- Client -> "client"
- Message -> "message"
"""

from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import List, Optional

# ------- Core Content Schemas -------

class Project(BaseModel):
    title: str = Field(..., description="Project title")
    category: str = Field(..., description="Gallery category, e.g., 'Branding', 'Animation', 'Motion', '3D', 'Social'"
    )
    description: Optional[str] = Field(None, description="Short description")
    image_url: Optional[HttpUrl] = Field(
        None, description="Thumbnail or cover image URL"
    )
    video_url: Optional[HttpUrl] = Field(
        None, description="Optional video or embed URL"
    )
    tags: List[str] = Field(default_factory=list, description="Tags for filtering")
    featured: bool = Field(False, description="Showcase on top")
    order: Optional[int] = Field(None, description="Manual sort order")

class Testimonial(BaseModel):
    name: str = Field(..., description="Person's name")
    role: Optional[str] = Field(None, description="Role/Title")
    company: Optional[str] = Field(None, description="Company name")
    quote: str = Field(..., description="Testimonial text")
    avatar_url: Optional[HttpUrl] = Field(None, description="Avatar image URL")

class Client(BaseModel):
    name: str = Field(..., description="Client brand name")
    website: Optional[HttpUrl] = Field(None, description="Client website")
    logo_url: Optional[HttpUrl] = Field(None, description="Logo image URL")

class Message(BaseModel):
    name: str = Field(..., description="Sender name")
    email: EmailStr = Field(..., description="Sender email")
    company: Optional[str] = Field(None, description="Company (optional)")
    message: str = Field(..., description="Message body")

# Expose a simple schema map for tooling (optional)
SCHEMAS = {
    "project": Project.model_json_schema(),
    "testimonial": Testimonial.model_json_schema(),
    "client": Client.model_json_schema(),
    "message": Message.model_json_schema(),
}
