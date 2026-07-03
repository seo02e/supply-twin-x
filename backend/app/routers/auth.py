from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import User, Company
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")

    company = db.query(Company).filter(Company.id == user.company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="회사를 찾을 수 없습니다.")

    new_user = User(
        email=user.email,
        username=user.username,
        password_hash=hash_password(user.password),
        company_id=user.company_id,
        role="COMPANY_ADMIN",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    access_token = create_access_token(
        data={
            "sub": str(db_user.id),
            "company_id": db_user.company_id,
            "role": db_user.role,
        }
    )

    company = db.query(Company).filter(Company.id == db_user.company_id).first()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "company_id": db_user.company_id,
        "company_name": company.company_name if company else "",
        "role": db_user.role,
        "username": db_user.username,
    }