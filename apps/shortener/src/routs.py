from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import HttpUrl
from database import get_session
from schemas import CreateLink, CreateLinkOut
from models import Link
from config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import services
import logging

logger = logging.getLogger("api_logger")
router = APIRouter()

@router.get("/healthz", status_code=status.HTTP_200_OK)
async def liveness():
    return {"status": "alive"}


@router.get("/readyz")
async def readiness(
    session: AsyncSession = Depends(get_session)
):
    try:
        await session.execute("SELECT 1")
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not ready"})
    return {"status": "ready"}


@router.post("/short", status_code=status.HTTP_201_CREATED, response_model=CreateLinkOut)
async def create_shorted_link(
    data: CreateLink,
    session: AsyncSession = Depends(get_session)
):
    logger.info("Requested shorted link creation for url: %s", data.original_url)
    short_code = await services.LinkService(session).create_link(str(data.original_url))
    return CreateLinkOut(
        original_url=data.original_url,
        shorted_url=HttpUrl(f"{settings.normalized_base_url}/{short_code}")
    )


@router.post("/{short_hash}", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect(
    short_hash: str,
    session: AsyncSession = Depends(get_session)
):
    query = select(Link).where(Link.short_hash == short_hash)
    result = await session.execute(query)
    link = result.scalar_one_or_none()

    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")

    return {"redirect_to": link.original_url}
