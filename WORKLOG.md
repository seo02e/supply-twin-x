# Work Log

## 2026-07-04 (금요일)

### 변경 파일

- **`backend/requirements.txt`**
  - `anthropic>=0.50.0` 패키지 추가

- **`backend/app/services/risk_service.py`**
  - `import json`, `os`, `datetime`, `anthropic` 추가
  - `_get_cached_report()` 함수 추가 — 동일 `company_id` + `risk_level` 24시간 이내 캐시 조회
  - `_llm_ai_report()` 함수 추가 — `claude-opus-4-8` 호출 (3초 타임아웃), 실패 시 규칙 기반 폴백 자동 적용
  - `calculate_company_risk()` — 캐시 우선 확인 후 캐시 미스 시 LLM 호출하도록 로직 변경

### 버그 수정 및 AI 리스크 엔진 프론트 연동

- **`backend/app/services/supplier_service.py`, `purchase_order_service.py`, `production_service.py`**
  - 단일 조회 함수(`get_supplier`/`get_purchase_order`/`get_production`) 누락으로 GET-by-id, `update_*`, `delete_*`가 전부 `NameError`로 500 에러 발생하던 버그 수정
  - `company_id` 없이 전체 조회하던 죽은 코드(중복 `get_suppliers`/`get_purchase_orders`/`get_productions`) 제거

- **`frontend/src/pages/Inventory.jsx`, `Supplier.jsx`, `PurchaseOrder.jsx`, `Production.jsx`**
  - "수정" 버튼을 눌러도 폼 제출 시 항상 `POST`(신규 생성)만 호출되던 문제 수정 — `editingId` 상태를 추가해 수정 모드일 때 `PUT`을 호출하도록 변경, 취소 버튼 추가

- **`frontend/src/pages/Risk.jsx`, `Dashboard.jsx`**
  - 프론트에 하드코딩되어 있던 목업 리스크 점수 계산 로직 제거, 백엔드 `/risk/summary`(Claude 기반 AI 리포트) 호출 결과로 대체
