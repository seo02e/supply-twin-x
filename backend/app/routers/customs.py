from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.models.models import User
from app.services.customs_service import get_customs_import_export

router = APIRouter(
    prefix="/customs",
    tags=["Customs"]
)


@router.get("/imports")
def get_customs_data(
    strtYymm: int = Query(..., example=202601),
    endYymm: int = Query(..., example=202606),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return get_customs_import_export(
            db=db,
            company_id=current_user.company_id,
            strtYymm=strtYymm,
            endYymm=endYymm,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))