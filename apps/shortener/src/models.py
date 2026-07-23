from database import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(primary_key=True)
    short_hash: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    original_url: Mapped[str] = mapped_column()
