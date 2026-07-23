import logging
import secrets

from models import Link
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class LinkService:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session
        self.logger: logging.Logger = logging.getLogger("link_service_logger")

    async def create_link(self, original: str) -> str:
        random_hash = secrets.token_urlsafe(10)
        self.logger.debug("Generated hash: %s", original)
        new_link = Link(short_hash=random_hash, original_url=original)

        self.session.add(new_link)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            self.logger.warning("Hash already exists. Trying another")
            return await self.create_link(original)

        await self.session.refresh(new_link)
        return random_hash
