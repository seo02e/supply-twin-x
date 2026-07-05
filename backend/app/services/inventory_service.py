from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.models import Inventory
from app.schemas.inventory import InventoryCreate, InventoryUpdate


def find_hscode_by_material(material_name: str, db: Session):
    if not material_name:
        return None

    row = db.execute(text("""
        SELECT hs_code
        FROM hs_codes
        WHERE item_name ILIKE :pattern
        ORDER BY id ASC
        LIMIT 1
    """), {"pattern": f"%{material_name}%"}).mappings().first()

    return row["hs_code"] if row else None


def create_inventory(db: Session, inventory: InventoryCreate, company_id: int):
    data = inventory.model_dump()
    data["company_id"] = company_id

    if not data.get("hs_code"):
        data["hs_code"] = find_hscode_by_material(data.get("material_name"), db)

    elif len(str(data.get("hs_code"))) < 10:
        auto_hs_code = find_hscode_by_material(data.get("material_name"), db)
        if auto_hs_code:
            data["hs_code"] = auto_hs_code

    new_inventory = Inventory(**data)

    db.add(new_inventory)
    db.commit()
    db.refresh(new_inventory)

    return new_inventory


def get_inventories(db: Session, company_id: int):
    return (
        db.query(Inventory)
        .filter(Inventory.company_id == company_id)
        .all()
    )


def get_inventory(db: Session, inventory_id: int):
    return db.query(Inventory).filter(Inventory.id == inventory_id).first()


def update_inventory(db: Session, inventory_id: int, inventory: InventoryUpdate):
    db_inventory = get_inventory(db, inventory_id)

    if not db_inventory:
        return None

    data = inventory.model_dump(exclude_unset=True)

    if data.get("material_name") and not data.get("hs_code"):
        data["hs_code"] = find_hscode_by_material(data.get("material_name"), db)

    if data.get("hs_code") and len(str(data["hs_code"])) < 10:
        material_name = data.get("material_name") or db_inventory.material_name
        auto_hs_code = find_hscode_by_material(material_name, db)
        if auto_hs_code:
            data["hs_code"] = auto_hs_code

    for key, value in data.items():
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
