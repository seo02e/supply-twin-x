from sqlalchemy.orm import Session
from pathlib import Path
import pandas as pd

from app.models.models import Inventory
from app.schemas.inventory import InventoryCreate, InventoryUpdate


BASE_DIR = Path(__file__).resolve().parents[2]
HSCODE_CSV_PATH = BASE_DIR / "data" / "processed" / "hscode_clean.csv"


def find_hscode_by_material(material_name: str):
    if not material_name:
        return None

    if not HSCODE_CSV_PATH.exists():
        return None

    df = pd.read_csv(HSCODE_CSV_PATH, dtype=str).fillna("")

    code_col = "hs_code"
    name_col = "item_name"

    matched = df[
        df[name_col].str.contains(material_name, case=False, na=False)
    ]

    if matched.empty:
        return None

    return matched.iloc[0][code_col]


def create_inventory(db: Session, inventory: InventoryCreate, company_id: int):
    data = inventory.model_dump()
    data["company_id"] = company_id

    if not data.get("hs_code"):
        data["hs_code"] = find_hscode_by_material(data.get("material_name"))

    elif len(str(data.get("hs_code"))) < 10:
        auto_hs_code = find_hscode_by_material(data.get("material_name"))
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
        data["hs_code"] = find_hscode_by_material(data.get("material_name"))

    if data.get("hs_code") and len(str(data["hs_code"])) < 10:
        material_name = data.get("material_name") or db_inventory.material_name
        auto_hs_code = find_hscode_by_material(material_name)
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