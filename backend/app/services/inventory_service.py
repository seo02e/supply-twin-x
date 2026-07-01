from sqlalchemy.orm import Session

from app.models.models import Inventory
from app.schemas.inventory import InventoryCreate, InventoryUpdate


def create_inventory(db: Session, inventory: InventoryCreate):
    db_inventory = Inventory(**inventory.model_dump())

    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)

    return db_inventory


def get_inventories(db: Session):
    return db.query(Inventory).all()


def get_inventory(db: Session, inventory_id: int):
    return (
        db.query(Inventory)
        .filter(Inventory.id == inventory_id)
        .first()
    )


def update_inventory(db: Session, inventory_id: int, inventory: InventoryUpdate):
    db_inventory = get_inventory(db, inventory_id)

    if not db_inventory:
        return None

    update_data = inventory.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_inventory, key, value)

    db.commit()
    db.refresh(db_inventory)

    return db_inventory


def delete_inventory(db: Session, inventory_id: int):
    db_inventory = get_inventory(db, inventory_id)

    if not db_inventory:
        return None

    db.delete(db_inventory)
    db.commit()

    return db_inventory