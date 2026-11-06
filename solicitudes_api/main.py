"""API de Solicitudes de Medicamentos  ->  uvicorn main:app --reload --port 8002"""
import logging
import math
import os

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from errors import configure_logging, register_error_handlers

configure_logging()  # antes de importar database, para que el log del túnel SSH ya tenga formato

from database import get_db  # noqa: E402
from models import Medication, Request  # noqa: E402
from schemas import MedicationOut, Page, RequestCreate, RequestOut  # noqa: E402
from security import get_current_user_id  # noqa: E402

logger = logging.getLogger("app.requests")

app = FastAPI(title="Solicitudes API", version="1.0.0")

register_error_handlers(app)  # debe ir antes de CORSMiddleware (ver errors.py)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")],
    allow_methods=["*"],
    allow_headers=["*"],
)

NO_POS_FIELDS = ("order_number", "address", "phone", "email")
FIELD_LABELS = {"order_number": "número de orden", "address": "dirección", "phone": "teléfono", "email": "correo electrónico"}


@app.get("/medications", response_model=list[MedicationOut])
def list_medications(
    db: Session = Depends(get_db),
    _user_id: int = Depends(get_current_user_id),
):
    return db.scalars(select(Medication).order_by(Medication.name)).all()


@app.post("/requests", response_model=RequestOut, status_code=status.HTTP_201_CREATED)
def create_request(
    data: RequestCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    medication = db.get(Medication, data.medication_id)
    if not medication:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "El medicamento no existe")

    values = data.model_dump()
    if medication.is_pos:
        # Para POS no se guardan los datos adicionales aunque el cliente los envíe
        for field in NO_POS_FIELDS:
            values[field] = None
    else:
        missing = [f for f in NO_POS_FIELDS if not values[f]]
        if missing:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Para medicamentos NO POS son obligatorios: {', '.join(FIELD_LABELS[f] for f in missing)}",
            )

    request = Request(user_id=user_id, **values)
    db.add(request)
    db.commit()
    db.refresh(request)
    logger.info("Solicitud creada id=%s usuario=%s medicamento=%s (%s)",
                request.id, user_id, medication.id, "POS" if medication.is_pos else "NO POS")
    return request


@app.get("/requests", response_model=Page)
def list_requests(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    belongs_to_user = Request.user_id == user_id
    total = db.scalar(select(func.count()).select_from(Request).where(belongs_to_user))

    items = db.scalars(
        select(Request)
        .where(belongs_to_user)
        .order_by(Request.created_at.desc(), Request.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()

    return Page(items=items, total=total, page=page, size=size, pages=max(1, math.ceil(total / size)))


@app.get("/health")
def health():
    return {"status": "ok"}
