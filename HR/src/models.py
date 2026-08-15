from datetime import date, datetime
from sqlalchemy import String, Text, Date, DateTime, Integer, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    company: Mapped[str | None] = mapped_column(Text)
    salary: Mapped[str | None] = mapped_column(String(200))
    location: Mapped[str | None] = mapped_column(String(200))
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="new")
    cover_text: Mapped[str | None] = mapped_column(Text)
    first_seen: Mapped[date] = mapped_column(Date, nullable=False)
    last_seen: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<Vacancy {self.id}: {self.title}>"


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20), default="running")
    hh_count: Mapped[int | None] = mapped_column(Integer)
    habr_count: Mapped[int | None] = mapped_column(Integer)
    total_vacancies: Mapped[int | None] = mapped_column(Integer)
    new_today: Mapped[int | None] = mapped_column(Integer)
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)

    def __repr__(self):
        return f"<PipelineRun #{self.id} {self.status} @ {self.started_at}>"
