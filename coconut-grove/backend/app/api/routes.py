from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from ..repositories.catalog import CatalogRepository
from ..schemas import ARRead, DishRead, MenuRead, ReviewsRead
from ..services.catalog import CatalogService
from pydantic import StringConstraints

router = APIRouter(prefix="/api/v1/restaurants/{restaurant_id}", tags=["Menu"])


def get_session(request: Request):
    # A fresh session per request; never share mutable sessions between guests.
    with Session(request.app.state.engine) as session:
        yield session


def get_catalog(session: Annotated[Session, Depends(get_session)]):
    return CatalogService(CatalogRepository(session))


Catalog = Annotated[CatalogService, Depends(get_catalog)]


@router.get("/menu", response_model=MenuRead)
def menu(
    restaurant_id: str, catalog: Catalog,
    q: Annotated[str, Query(max_length=100)] = "",
    category: Annotated[str | None, Query(max_length=100)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 24,
    offset: Annotated[int, Query(ge=0)] = 0,
    dish_ids: Annotated[list[Annotated[str, StringConstraints(max_length=100)]] | None, Query(max_length=100)] = None,
):
    return catalog.menu(restaurant_id, q, category, limit, offset, dish_ids)


@router.get("/dishes/{dish_id}", response_model=DishRead)
def dish(restaurant_id: str, dish_id: str, catalog: Catalog):
    return catalog.dish(restaurant_id, dish_id)


@router.get("/dishes/{dish_id}/reviews", response_model=ReviewsRead)
def reviews(restaurant_id: str, dish_id: str, catalog: Catalog):
    catalog.dish(restaurant_id, dish_id)
    return ReviewsRead()


@router.get("/dishes/{dish_id}/ar", response_model=ARRead)
def ar(restaurant_id: str, dish_id: str, catalog: Catalog):
    catalog.dish(restaurant_id, dish_id)
    return ARRead()
