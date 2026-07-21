from database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(primary_key=True)
    short_hash: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    original_url: Mapped[str] = mapped_column()
