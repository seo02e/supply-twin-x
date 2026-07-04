-- =========================================================
-- Supply Twin-X Database Reset & Seed SQL
-- 목적:
-- 1) 공공데이터 적재 테이블은 유지
--    - crude_oil_prices
--    - material_prices
--    - industrial_complexes
--    - industry_trends
-- 2) API/ERP용 테이블은 models.py 기준으로 재생성
-- 3) 석유화학 MVP 테스트 데이터 삽입
-- 4) 환율 API 저장용 exchange_rates 테이블 생성
-- =========================================================


-- =========================================================
-- 1. 기존 API/ERP 관련 테이블 삭제
-- =========================================================
DROP TABLE IF EXISTS risk_histories CASCADE;
DROP TABLE IF EXISTS purchase_orders CASCADE;
DROP TABLE IF EXISTS productions CASCADE;
DROP TABLE IF EXISTS inventories CASCADE;
DROP TABLE IF EXISTS suppliers CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS companies CASCADE;
DROP TABLE IF EXISTS customs_trades CASCADE;

-- 과거 잘못 생성했던 테이블 제거
DROP TABLE IF EXISTS risk_results CASCADE;
DROP TABLE IF EXISTS company_materials CASCADE;
DROP TABLE IF EXISTS supply_chain_edges CASCADE;
DROP TABLE IF EXISTS customs_imports CASCADE;
DROP TABLE IF EXISTS exchange_rates CASCADE;


-- =========================================================
-- 2. 회사 테이블
-- =========================================================
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    business_number VARCHAR(50),
    industry_type VARCHAR(100),
    complex_id INTEGER REFERENCES industrial_complexes(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW()
);


-- =========================================================
-- 3. 사용자 테이블
-- =========================================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(100),
    role VARCHAR(30) DEFAULT 'COMPANY_ADMIN',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ix_users_email ON users(email);


-- =========================================================
-- 4. 공급업체 테이블
-- =========================================================
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    supplier_name VARCHAR(255),
    country VARCHAR(100),
    material_name VARCHAR(100),
    lead_time_days INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);


-- =========================================================
-- 5. 재고 테이블
-- =========================================================
CREATE TABLE inventories (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    material_name VARCHAR(100),
    hs_code VARCHAR(20),
    current_stock NUMERIC,
    safety_stock NUMERIC,
    daily_usage NUMERIC,
    unit VARCHAR(30),
    updated_at TIMESTAMP DEFAULT NOW()
);


-- =========================================================
-- 6. 발주 테이블
-- =========================================================
CREATE TABLE purchase_orders (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    supplier_id INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
    material_name VARCHAR(100),
    quantity NUMERIC,
    order_date DATE,
    expected_arrival_date DATE,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);


-- =========================================================
-- 7. 생산 테이블
-- =========================================================
CREATE TABLE productions (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    product_name VARCHAR(100),
    production_quantity NUMERIC,
    operation_rate NUMERIC,
    production_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);


-- =========================================================
-- 8. 관세/수출입 데이터 테이블
-- =========================================================
CREATE TABLE customs_trades (
    id SERIAL PRIMARY KEY,
    hs_code VARCHAR(20),
    item_name VARCHAR(255),
    country_name VARCHAR(100),
    import_amount NUMERIC,
    import_weight NUMERIC,
    export_amount NUMERIC,
    export_weight NUMERIC,
    trade_month VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);


-- =========================================================
-- 9. 리스크 이력 테이블
-- =========================================================
CREATE TABLE risk_histories (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    material_name VARCHAR(100),
    risk_score NUMERIC,
    risk_level VARCHAR(20),
    price_score NUMERIC,
    import_score NUMERIC,
    inventory_score NUMERIC,
    operation_score NUMERIC,
    oil_score NUMERIC,
    reason TEXT,
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);


-- =========================================================
-- 10. 환율 테이블
-- =========================================================
CREATE TABLE exchange_rates (
    id SERIAL PRIMARY KEY,
    currency_code VARCHAR(20) NOT NULL,
    currency_name VARCHAR(100),
    base_rate NUMERIC,
    rate_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ix_exchange_rates_currency_date
ON exchange_rates(currency_code, rate_date);


-- =========================================================
-- 11. 테스트 회사 데이터
-- =========================================================
INSERT INTO companies (
    id,
    company_name,
    business_number,
    industry_type,
    complex_id
)
VALUES (
    1,
    '테스트 석유화학 회사',
    '123-45-67890',
    '석유화학',
    NULL
);


-- =========================================================
-- 12. 석유화학 MVP 더미데이터
-- =========================================================

-- 공급업체
INSERT INTO suppliers (
    company_id,
    supplier_name,
    country,
    material_name,
    lead_time_days
)
VALUES
(1, 'Saudi Aramco', 'Saudi Arabia', '원유', 35),
(1, 'Kuwait Petroleum', 'Kuwait', '나프타', 28),
(1, 'ADNOC', 'UAE', '윤활기유', 32);


-- 재고
INSERT INTO inventories (
    company_id,
    material_name,
    hs_code,
    current_stock,
    safety_stock,
    daily_usage,
    unit
)
VALUES
(1, '원유', '2709', 4200, 5000, 250, 'barrel'),
(1, '나프타', '2710', 1800, 2500, 120, 'ton'),
(1, '윤활기유', '2710', 900, 800, 45, 'ton');


-- 발주
INSERT INTO purchase_orders (
    company_id,
    supplier_id,
    material_name,
    quantity,
    order_date,
    expected_arrival_date,
    status
)
VALUES
(1, 1, '원유', 10000, '2026-06-20', '2026-07-20', 'ORDERED'),
(1, 2, '나프타', 5000, '2026-06-10', '2026-07-01', 'DELAYED'),
(1, 3, '윤활기유', 2000, '2026-06-25', '2026-07-10', 'ORDERED');


-- 생산
INSERT INTO productions (
    company_id,
    product_name,
    production_quantity,
    operation_rate,
    production_date
)
VALUES
(1, '석유화학 기초유분', 1200, 72.5, '2026-07-03'),
(1, '나프타 분해 제품', 850, 68.0, '2026-07-03'),
(1, '윤활유 제품', 430, 81.0, '2026-07-03');


-- =========================================================
-- 13. 시퀀스 정렬
-- 수동으로 id=1 회사를 넣었기 때문에 다음 INSERT 충돌 방지
-- =========================================================
SELECT setval(
    pg_get_serial_sequence('companies', 'id'),
    COALESCE((SELECT MAX(id) FROM companies), 1)
);


-- =========================================================
-- 14. 확인용 SELECT
-- =========================================================
SELECT 'companies' AS table_name, COUNT(*) AS count FROM companies
UNION ALL
SELECT 'suppliers', COUNT(*) FROM suppliers
UNION ALL
SELECT 'inventories', COUNT(*) FROM inventories
UNION ALL
SELECT 'purchase_orders', COUNT(*) FROM purchase_orders
UNION ALL
SELECT 'productions', COUNT(*) FROM productions
UNION ALL
SELECT 'exchange_rates', COUNT(*) FROM exchange_rates;
