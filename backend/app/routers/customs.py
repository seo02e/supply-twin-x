from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.customs_service import get_customs_import_export

router = APIRouter(
    prefix="/customs",
    tags=["Customs"]
)


@router.get("/imports")
def get_customs_data(
    company_id: int = Query(..., example=1),
    strtYymm: int = Query(..., example=202601),
    endYymm: int = Query(..., example=202606),
    db: Session = Depends(get_db),
):
    try:
        return get_customs_import_export(
            db=db,
            company_id=company_id,
            strtYymm=strtYymm,
            endYymm=endYymm,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))