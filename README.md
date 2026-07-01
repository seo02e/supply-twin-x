python = 3.13.9

백엔드
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
( 백엔드 서버 실행 )
uvicorn app.main:app --reload

루트에서
docker compose up -d

디비버에서
sql편집기 실행 후

루트에서
python data/scripts/preprocess_complex.py
python data/scripts/preprocess_trend.py
python data/scripts/preprocess_material.py
python data/scripts/load_to_db.py

```
데이터
관세청 품목별 수출입실적 (API/) -> 수입량 변화
전국산업단지현황통계_국가산업단지 (파일데이터/최신4월10) -> 산업단지 정보
국가산업단지 산업동향정보 (파일데이터/5월27) -> 생산 수출 가동률
조달청_홈페이지_비축물자_원자재_일일가격 (파일데이터/25년11월6일) -> 가격예측

(추가예정)
환율정보
관세청 HS코드/품목명 매핑
```
