import { useEffect, useMemo, useState } from "react";
import api from "../services/api";

function Supplier() {
  const [suppliers, setSuppliers] = useState([]);
  const [keyword, setKeyword] = useState("");
  const [editingId, setEditingId] = useState(null);

  const [form, setForm] = useState({
    supplier_name: "",
    country: "",
    material_name: "",
    lead_time_days: "",
  });

  const fetchSuppliers = async () => {
    const companyId = localStorage.getItem("company_id");
    const res = await api.get(`/suppliers/?company_id=${companyId}`);
    setSuppliers(res.data);
  };

  useEffect(() => {
    fetchSuppliers();
  }, []);

  const filteredSuppliers = useMemo(() => {
    return suppliers.filter((item) => {
      const text =
        `${item.supplier_name} ${item.country} ${item.material_name}`.toLowerCase();
      return text.includes(keyword.toLowerCase());
    });
  }, [suppliers, keyword]);

  const avgLeadTime = useMemo(() => {
    if (suppliers.length === 0) return 0;
    const total = suppliers.reduce(
      (sum, item) => sum + Number(item.lead_time_days || 0),
      0
    );
    return total / suppliers.length;
  }, [suppliers]);

  const riskCount = suppliers.filter(
    (item) => Number(item.lead_time_days) >= 30
  ).length;

  const getRiskStatus = (leadTime) => {
    const days = Number(leadTime);
    if (days >= 30) return "위험";
    if (days >= 20) return "주의";
    return "안정";
  };

  const getRiskScore = (leadTime) => {
    const days = Number(leadTime || 0);
    return Math.min((days / 40) * 100, 100);
  };

  const countrySummary = useMemo(() => {
    const map = {};

    suppliers.forEach((item) => {
      map[item.country] = (map[item.country] || 0) + 1;
    });

    return Object.entries(map).map(([country, count]) => ({
      country,
      count,
      ratio: suppliers.length ? (count / suppliers.length) * 100 : 0,
    }));
  }, [suppliers]);

  const mainCountry = countrySummary.length
    ? [...countrySummary].sort((a, b) => b.count - a.count)[0].country
    : "-";

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const resetForm = () => {
    setForm({
      supplier_name: "",
      country: "",
      material_name: "",
      lead_time_days: "",
    });
    setEditingId(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const companyId = localStorage.getItem("company_id");

    if (editingId) {
      await api.put(`/suppliers/${editingId}`, {
        supplier_name: form.supplier_name,
        country: form.country,
        material_name: form.material_name,
        lead_time_days: Number(form.lead_time_days),
      });
    } else {
      await api.post("/suppliers/", {
        company_id: Number(companyId),
        supplier_name: form.supplier_name,
        country: form.country,
        material_name: form.material_name,
        lead_time_days: Number(form.lead_time_days),
      });
    }

    resetForm();
    fetchSuppliers();
  };

  const handleEdit = (item) => {
    setForm({
      supplier_name: item.supplier_name,
      country: item.country,
      material_name: item.material_name,
      lead_time_days: item.lead_time_days,
    });
    setEditingId(item.id);
  };

  const handleDelete = async (id) => {
    await api.delete(`/suppliers/${id}`);
    if (editingId === id) resetForm();
    fetchSuppliers();
  };

  return (
    <div className="supplier-page">
      <div className="page-title">
        <h1>Suppliers</h1>
        <p>공급업체를 등록하고 공급망 위험 분석에 활용합니다.</p>
      </div>

      <div className="supplier-kpi-grid">
        <div className="supplier-kpi-card">
          <p>총 공급업체</p>
          <h2>{suppliers.length}개</h2>
        </div>
        <div className="supplier-kpi-card">
          <p>평균 Lead Time</p>
          <h2>{avgLeadTime.toFixed(1)}일</h2>
        </div>
        <div className="supplier-kpi-card danger">
          <p>위험 공급업체</p>
          <h2>{riskCount}개</h2>
        </div>
        <div className="supplier-kpi-card">
          <p>주요 의존 국가</p>
          <h2>{mainCountry}</h2>
        </div>
      </div>

      <div className="panel supplier-panel">
        <h3>공급업체 등록</h3>

        <form className="supplier-form" onSubmit={handleSubmit}>
          <input
            name="supplier_name"
            placeholder="공급업체명 예: Saudi Aramco"
            value={form.supplier_name}
            onChange={handleChange}
            required
          />

          <input
            name="country"
            placeholder="국가 예: Saudi Arabia"
            value={form.country}
            onChange={handleChange}
            required
          />

          <input
            name="material_name"
            placeholder="원자재 예: 원유"
            value={form.material_name}
            onChange={handleChange}
            required
          />

          <input
            name="lead_time_days"
            type="number"
            placeholder="Lead Time 예: 35"
            value={form.lead_time_days}
            onChange={handleChange}
            required
          />

          <button type="submit">{editingId ? "수정 저장" : "등록"}</button>
          {editingId && (
            <button type="button" className="cancel-btn" onClick={resetForm}>
              취소
            </button>
          )}
        </form>
      </div>

      <div className="panel table-panel supplier-panel">
        <div className="panel-header">
          <h3>공급업체 목록</h3>
          <input
            className="search-input"
            placeholder="공급업체, 국가, 원자재 검색..."
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
          />
        </div>

        <table className="supplier-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>공급업체</th>
              <th>국가</th>
              <th>원자재</th>
              <th>Lead Time</th>
              <th>공급 리스크</th>
              <th>리스크 지수</th>
              <th>관리</th>
            </tr>
          </thead>

          <tbody>
            {filteredSuppliers.map((item) => {
              const status = getRiskStatus(item.lead_time_days);
              const score = getRiskScore(item.lead_time_days);

              return (
                <tr key={item.id}>
                  <td>{item.id}</td>
                  <td className="supplier-name">{item.supplier_name}</td>
                  <td>{item.country}</td>
                  <td className="material-name">{item.material_name}</td>
                  <td>{item.lead_time_days}일</td>
                  <td>
                    <span className={`supplier-status ${status}`}>
                      {status}
                    </span>
                  </td>
                  <td>
                    <div className="risk-score-cell">
                      <span>{score.toFixed(0)}점</span>
                      <div className="risk-score-bar">
                        <div style={{ width: `${score}%` }} />
                      </div>
                    </div>
                  </td>
                  <td className="action-cell">
                    <button className="edit-btn" onClick={() => handleEdit(item)}>
                      수정
                    </button>
                    <button
                      className="delete-btn"
                      onClick={() => handleDelete(item.id)}
                    >
                      삭제
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {filteredSuppliers.length === 0 && (
          <p className="empty-text">등록된 공급업체가 없습니다.</p>
        )}
      </div>

      <div className="panel supplier-panel dependency-panel">
        <h3>국가별 공급 의존도</h3>

        <div className="dependency-list">
          {countrySummary.map((item) => (
            <div className="dependency-item" key={item.country}>
              <div>
                <strong>{item.country}</strong>
                <p>공급업체 {item.count}개</p>
              </div>
              <div className="dependency-bar-wrap">
                <span>{item.ratio.toFixed(1)}%</span>
                <div className="dependency-bar">
                  <div style={{ width: `${item.ratio}%` }} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Supplier;