# This module will define the data models for UML classes and attributes.
from pydantic import BaseModel

class UmlClassAttribute(BaseModel):
    name: str
    type: str
    format: str | None = None
    description: str | None = None
    example: str | None = None
    required: bool = False
    ref: str | None = None

class UmlClass(BaseModel):
    name: str
    type: str = "class"
    attributes: list[UmlClassAttribute] = []
    description: str | None = None

class UmlRelationship(BaseModel):
    source: UmlClass
    target: UmlClass
    name: str | None = None
    type: str = "association"  # or "composition", "aggregation", etc.
    description: str | None = None
    multiplicitySource: str | None = None  # e.g., "1..*", "0..1", etc.
    multiplicityTarget: str | None = None  # e.g., "1..*", "0..1", etc.