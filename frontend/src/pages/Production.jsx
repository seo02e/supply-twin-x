import { useEffect, useMemo, useState } from "react";
import api from "../services/api";

function Production() {
  const [productions, setProductions] = useState([]);
  const [keyword, setKeyword] = useState("");

  const [form, setForm] = useState({
    company_id: 1,
    product_name: "",
    production_quantity: "",
    operation_rate: "",
    production_date: "",
  });

  const fetchProductions = async () => {
    const res = await api.get("/productions/");
    setProductions(res.data);
  };

  useEffect(() => {
    fetchProductions();
  }, []);

  const filteredProductions = useMemo(() => {
    return productions.filter((item) =>
      `${item.product_name} ${item.production_date}`
        .toLowerCase()
        .includes(keyword.toLowerCase())
    );
  }, [productions, keyword]);

  const totalQuantity = useMemo(() => {
    return productions.reduce(
      (sum, item) => sum + Number(item.production_quantity || 0),
      0
    );
  }, [productions]);

  const avgOperationRate = useMemo(() => {
    if (productions.length === 0) return 0;
    const total = productions.reduce(
      (sum, item) => sum + Number(item.operation_rate || 0),
      0
    );
    return total / productions.length;
  }, [productions]);

  const getProductionStatus = (rate) => {
    const value = Number(rate);
    if (value < 70) return "위험";
    if (value < 85) return "주의";
    return "정상";
  };

  const getRiskScore = (rate) => {
    const value = Number(rate || 0);
    return Math.max(100 - value, 0);
  };

  const riskCount = productions.filter(
    (item) => getProductionStatus(item.operation_rate) === "위험"
  ).length;

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    await api.post("/productions/", {
      ...form,
      company_id: Number(form.company_id),
      production_quantity: Number(form.production_quantity),
      operation_rate: Number(form.operation_rate),
    });

    setForm({
      company_id: 1,
      product_name: "",
      production_quantity: "",
      operation_rate: "",
      production_date: "",
    });

    fetchProductions();
  };

  const handleEdit = (item) => {
    setForm({
      company_id: item.company_id,
      product_name: item.product_name,
      production_quantity: item.production_quantity,
      operation_rate: item.operation_rate,
      production_date: item.production_date,
    });
  };

  const handleDelete = async (id) => {
    await api.delete(`/productions/${id}`);
    fetchProductions();
  };

  return (
    <div className="production-page">
      <div className="page-title">
        <h1>Productions</h1>
        <p>생산량과 가동률 데이터를 등록하고 생산 중단 위험 분석에 활용합니다.</p>
      </div>

      <div className="production-kpi-grid">
        <div className="production-kpi-card">
          <p>총 생산 제품</p>
          <h2>{productions.length}개</h2>
        </div>
        <div className="production-kpi-card">
          <p>총 생산량</p>
          <h2>{totalQuantity.toLocaleString()}</h2>
        </div>
        <div className="production-kpi-card">
          <p>평균 가동률</p>
          <h2>{avgOperationRate.toFixed(1)}%</h2>
        </div>
        <div className="production-kpi-card danger">
          <p>위험 생산라인</p>
          <h2>{riskCount}개</h2>
        </div>
      </div>

      <div className="panel production-panel">
        <h3>생산 데이터 등록</h3>

        <form className="production-form" onSubmit={handleSubmit}>
          <input
            name="product_name"
            placeholder="제품명 예: 석유화학 기초유분"
            value={form.product_name}
            onChange={handleChange}
            required
          />

          <input
            name="production_quantity"
            type="number"
            placeholder="생산량"
            value={form.production_quantity}
            onChange={handleChange}
            required
          />

          <input
            name="operation_rate"
            type="number"
            step="0.1"
            placeholder="가동률 (%)"
            value={form.operation_rate}
            onChange={handleChange}
            required
          />

          <input
            name="production_date"
            type="date"
            value={form.production_date}
            onChange={handleChange}
            required
          />

          <button type="submit">등록 / 수정</button>
        </form>
      </div>

      <div className="panel table-panel production-panel">
        <div className="panel-header">
          <h3>생산 데이터 목록</h3>
          <input
            className="search-input"
            placeholder="제품명 또는 생산일자 검색..."
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
          />
        </div>

        <table className="production-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>제품명</th>
              <th>생산량</th>
              <th>가동률</th>
              <th>생산일자</th>
              <th>생산 상태</th>
              <th>중단 리스크</th>
              <th>관리</th>
            </tr>
          </thead>

          <tbody>
            {filteredProductions.map((item) => {
              const status = getProductionStatus(item.operation_rate);
              const score = getRiskScore(item.operation_rate);

              return (
                <tr key={item.id}>
                  <td>{item.id}</td>
                  <td className="product-name">{item.product_name}</td>
                  <td>{Number(item.production_quantity).toLocaleString()}</td>
                  <td>{item.operation_rate}%</td>
                  <td>{item.production_date}</td>
                  <td>
                    <span className={`production-status ${status}`}>
                      {status}
                    </span>
                  </td>
                  <td>
                    <div className="production-risk-cell">
                      <span>{score.toFixed(0)}점</span>
                      <div className="production-risk-bar">
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

        {filteredProductions.length === 0 && (
          <p className="empty-text">등록된 생산 데이터가 없습니다.</p>
        )}
      </div>
    </div>
  );
}

export default Production;