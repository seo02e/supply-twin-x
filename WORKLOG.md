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
