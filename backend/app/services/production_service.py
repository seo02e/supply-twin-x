from sqlalchemy.orm import Session

from app.models.models import Production
from app.schemas.production import ProductionCreate, ProductionUpdate


def create_production(db: Session, production: ProductionCreate):
    db_production = Production(**production.model_dump())

    db.add(db_production)
    db.commit()
    db.refresh(db_production)

    return db_production


def get_productions(db: Session):
    return db.query(Production).all()


def get_productions(db: Session, company_id: int):
    return (
        db.query(Production)
        .filter(Production.company_id == company_id)
        .all()
    )

def update_production(
    db: Session,
    production_id: int,
    production: ProductionUpdate,
):
    db_production = get_production(db, production_id)

    if not db_production:
        return None

    update_data = production.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_production, key, value)

    db.commit()
    db.refresh(db_production)

    return db_production


def delete_production(db: Session, production_id: int):
    db_production = get_production(db, production_id)

    if not db_production:
        return None

    db.delete(db_production)
    db.commit()

    return db_production