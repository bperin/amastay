from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field
from models import *


class ScrapedResponse(BaseModel):
    """Model representing a scraped data in the system"""

    main_text: str = ""
    amenities: Optional[List[str]] = []
    reviews: Optional[List[str]] = []
    photos: Optional[List[str]] = []
