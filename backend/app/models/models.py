from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class IndustrialComplex(Base):
    __tablename__ = "industrial_complexes"

    id = Column(Integer, primary_key=True, index=True)
    complex_type = Column(String(50))
    province = Column(String(50))
    city = Column(String(50))
    complex_name = Column(String(255))
    development_status = Column(String(50))
    sale_rate = Column(Numeric)
    resident_companies = Column(Integer)
    active_companies = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

    companies = relationship("Company", back_populates="industrial_complex")


class IndustryTrend(Base):
    __tablename__ = "industry_trends"

    id = Column(Integer, primary_key=True, index=True)
    complex_name = Column(String(255))
    complex_type = Column(String(50))
    resident_current = Column(Integer)
    active_current = Column(Integer)
    production_current = Column(Numeric)
    production_change_rate = Column(Numeric)
    export_current = Column(Numeric)
    export_change_rate = Column(Numeric)
    operation_rate_current = Column(Numeric)
    created_at = Column(DateTime, server_default=func.now())


class MaterialPrice(Base):
    __tablename__ = "material_prices"

    id = Column(Integer, primary_key=True, index=True)
    material_name = Column(String(100))
    sales_office = Column(String(100))
    price = Column(Numeric)
    price_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())


class CustomsTrade(Base):
    __tablename__ = "customs_trades"

    id = Column(Integer, primary_key=True, index=True)
    hs_code = Column(String(20))
    item_name = Column(String(255))
    country_name = Column(String(100))
    import_amount = Column(Numeric)
    import_weight = Column(Numeric)
    export_amount = Column(Numeric)
    export_weight = Column(Numeric)
    trade_month = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    business_number = Column(String(50))
    industry_type = Column(String(100))
    complex_id = Column(Integer, ForeignKey("industrial_complexes.id", ondelete="SET NULL"))
    created_at = Column(DateTime, server_default=func.now())

    industrial_complex = relationship("IndustrialComplex", back_populates="companies")
    users = relationship("User", back_populates="company", cascade="all, delete")
    suppliers = relationship("Supplier", back_populates="company", cascade="all, delete")
    inventories = relationship("Inventory", back_populates="company", cascade="all, delete")
    purchase_orders = relationship("PurchaseOrder", back_populates="company", cascade="all, delete")
    productions = relationship("Production", back_populates="company", cascade="all, delete")
    risk_histories = relationship("RiskHistory", back_populates="company", cascade="all, delete")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(100))
    role = Column(String(30), default="COMPANY_ADMIN")
    created_at = Column(DateTime, server_default=func.now())

    company = relationship("Company", back_populates="users")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    supplier_name = Column(String(255))
    country = Column(String(100))
    material_name = Column(String(100))
    lead_time_days = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

    company = relationship("Company", back_populates="suppliers")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")


class Inventory(Base):
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    material_name = Column(String(100))
    hs_code = Column(String(20))
    current_stock = Column(Numeric)
    safety_stock = Column(Numeric)
    daily_usage = Column(Numeric)
    unit = Column(String(30))
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    company = relationship("Company", back_populates="inventories")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"))
    material_name = Column(String(100))
    quantity = Column(Numeric)
    order_date = Column(Date)
    expected_arrival_date = Column(Date)
    status = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

    company = relationship("Company", back_populates="purchase_orders")
    supplier = relationship("Supplier", back_populates="purchase_orders")


class Production(Base):
    __tablename__ = "productions"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    product_name = Column(String(100))
    production_quantity = Column(Numeric)
    operation_rate = Column(Numeric)
    production_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())

    company = relationship("Company", back_populates="productions")


class RiskHistory(Base):
    __tablename__ = "risk_histories"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    material_name = Column(String(100))
    risk_score = Column(Numeric)
    risk_level = Column(String(20))
    price_score = Column(Numeric)
    import_score = Column(Numeric)
    inventory_score = Column(Numeric)
    operation_score = Column(Numeric)
    reason = Column(Text)
    recommendation = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    company = relationship("Company", back_populates="risk_histories")