from fastapi import APIRouter, HTTPException, Query

from app.services.customs_service import get_customs_import_export

router = APIRouter(
    prefix="/customs",
    tags=["Customs"]
)


@router.get("/imports")
def get_customs_data(
    strtYymm: int = Query(..., example=202601),
    endYymm: int = Query(..., example=202606),
    hsSgn: int | None = Query(None, example=283691),
):
    try:
        return get_customs_import_export(strtYymm, endYymm, hsSgn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))