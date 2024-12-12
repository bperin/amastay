from pydantic import BaseModel, HttpUrl
from uuid import UUID
from typing import Optional


class CreatePropertyInput(BaseModel):
    name: str
    address: str
    description: Optional[str] = None
    property_url: HttpUrl
    manager_id: Optional[UUID] = None

    class Config:
        json_schema_extra = {"example": {"name": "Sunset Villa", "address": "123 Ocean Drive", "description": "Beautiful beachfront property", "property_url": "https://example.com/property/123", "manager_id": "123e4567-e89b-12d3-a456-426614174001"}}


class UpdatePropertyInput(BaseModel):
    id: UUID
    name: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    property_url: Optional[HttpUrl] = None
    manager_id: Optional[UUID] = None

    class Config:
        json_schema_extra = {"example": {"id": "123e4567-e89b-12d3-a456-426614174000", "name": "Updated Villa Name", "address": "124 Ocean Drive", "description": "Updated description", "property_url": "https://example.com/property/124", "manager_id": "123e4567-e89b-12d3-a456-426614174001"}}


class AddPropertyInfoInput(BaseModel):
    property_id: UUID
    name: str
    detail: str
    is_recommendation: bool
    metadata_url: Optional[HttpUrl] = None
    category_id: Optional[UUID] = None

    class Config:
        json_schema_extra = {"example": {"property_id": "123e4567-e89b-12d3-a456-426614174000", "name": "Pool Access", "detail": "24/7 access to infinity pool", "is_recommendation": True, "metadata_url": "https://example.com/metadata/123", "category_id": "123e4567-e89b-12d3-a456-426614174002"}}


class UpdatePropertyInfoInput(BaseModel):
    id: UUID
    name: Optional[str] = None
    detail: Optional[str] = None
    is_recommendation: Optional[bool] = None

    class Config:
        json_schema_extra = {"example": {"id": "123e4567-e89b-12d3-a456-426614174000", "name": "Updated Pool Access", "detail": "Pool access from 6 AM to 10 PM", "is_recommendation": False}}
