from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RestaurantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    location: str
    instagram_url: str
    currency: str


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str


class PortionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    label: str
    quantity: str
    price_minor: int | None = Field(default=None, ge=0)


class DishRead(BaseModel):
    id: str
    name: str
    description: str
    category: str
    image_url: str
    ingredients: list[str]
    example_allergens: str
    preparation_minutes: tuple[int, int] | None
    spice_level: int | None = Field(default=None, ge=0, le=5)
    source_url: str | None = None
    source_observed_on: str | None = None
    is_sample: bool
    ar_status: Literal["planned"] = "planned"
    portions: list[PortionRead]


class MenuRead(BaseModel):
    restaurant: RestaurantRead
    categories: list[CategoryRead]
    dishes: list[DishRead]
    total: int
    limit: int
    offset: int


class ReviewsRead(BaseModel):
    status: Literal["planned"] = "planned"
    reviews: list[dict] = []
    message: str = "Verified reviews and moderation are planned. No public submissions are accepted."


class ARRead(BaseModel):
    status: Literal["planned"] = "planned"
    model_urls: list[str] = []
    requirements: list[str] = [
        "Restaurant-approved 3D models for each dish and portion.",
        "Measured serving dimensions for a credible life-sized preview.",
        "AR integration and testing on supported iPhone and Android devices.",
    ]
