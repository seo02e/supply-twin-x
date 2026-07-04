import { useEffect, useMemo, useState } from "react";
import api from "../services/api";

function Inventory() {
  const [inventories, setInventories] = useState([]);
  const [keyword, setKeyword] = useState("");

  const [form, setForm] = useState({
    material_name: "",
    current_stock: "",
    safety_stock: "",
    daily_usage: "",
    unit: "kg",
  });

  const fetchInventories = async () => {
    const companyId = localStorage.getItem("company_id");
    const res = await api.get(`/inventory/?company_id=${companyId}`);
    setInventories(res.data);
  };

  useEffect(() => {
    fetchInventories();
  }, []);

  const totalStock = useMemo(() => {
    return inventories.reduce(
      (sum, item) => sum + Number(item.current_stock || 0),
      0
    );
  }, [inventories]);

  const filteredInventories = useMemo(() => {
    return inventories.filter((item) => {
      const text =
        `${item.material_name} ${item.hs_code || ""} ${item.unit}`.toLowerCase();
      return text.includes(keyword.toLowerCase());
    });
  }, [inventories, keyword]);

  const getRemainDays = (item) => {
    const stock = Number(item.current_stock || 0);
    const usage = Number(item.daily_usage || 0);
    if (usage === 0) return 0;
    return stock / usage;
  };

  const getImportance = (item) => {
    if (totalStock === 0) return 0;
    return (Number(item.current_stock || 0) / totalStock) * 100;
  };

  const getStatus = (item) => {
    const stock = Number(item.current_stock);
    const safety = Number(item.safety_stock);

    if (stock < safety) return "위험";
    if (stock < safety * 1.2) return "주의";
    return "정상";
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm({
      ...form,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const companyId = localStorage.getItem("company_id");

    await api.post("/inventory/", {
      company_id: Number(companyId),
      material_name: form.material_name,
      current_stock: Number(form.current_stock),
      safety_stock: Number(form.safety_stock),
      daily_usage: Number(form.daily_usage),
      unit: form.unit,
      hs_code: "",
    });

    setForm({
      material_name: "",
      current_stock: "",
      safety_stock: "",
      daily_usage: "",
      unit: "kg",
    });

    fetchInventories();
  };

  const handleEdit = (item) => {
    setForm({
      material_name: item.material_name,
      current_stock: item.current_stock,
      safety_stock: item.safety_stock,
      daily_usage: item.daily_usage,
      unit: item.unit,
    });
  };

  const handleDelete = async (id) => {
    await api.delete(`/inventory/${id}`);
    fetchInventories();
  };

  return (
    <div className="inventory-page">
      <div className="page-title">
        <h1>Inventory</h1>
        <p>재고 데이터를 등록하고 공급망 위험 분석에 활용합니다.</p>
      </div>

      <div className="panel inventory-panel">
        <h3>재고 등록</h3>

        <form className="form-grid inventory-form" onSubmit={handleSubmit}>
          <input
            name="material_name"
            placeholder="원자재명 예: 원유"
            value={form.material_name}
            onChange={handleChange}
            required
          />

          <input
            name="current_stock"
            type="number"
            placeholder="현재 재고"
            value={form.current_stock}
            onChange={handleChange}
            required
          />

          <input
            name="safety_stock"
            type="number"
            placeholder="안전 재고"
            value={form.safety_stock}
            onChange={handleChange}
            required
          />

          <input
            name="daily_usage"
            type="number"
            placeholder="일일 사용량"
            value={form.daily_usage}
            onChange={handleChange}
            required
          />

          <input
            name="unit"
            placeholder="단위"
            value={form.unit}
            onChange={handleChange}
            required
          />

          <button type="submit">재고 등록 / 수정</button>
        </form>
      </div>

      <div className="panel table-panel inventory-panel">
        <div className="panel-header">
          <h3>재고 목록</h3>
          <input
            className="search-input"
            placeholder="원자재명 또는 HS Code 검색..."
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
          />
        </div>

        <table className="inventory-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>원자재명</th>
              <th>HS Code</th>
              <th>현재 재고</th>
              <th>안전 재고</th>
              <th>일일 사용량</th>
              <th>단위</th>
              <th>남은 일수</th>
              <th>상태</th>
              <th>비율/중요도</th>
              <th>관리</th>
            </tr>
          </thead>

          <tbody>
            {filteredInventories.map((item) => {
              const importance = getImportance(item);
              const remainDays = getRemainDays(item);
              const status = getStatus(item);

              return (
                <tr key={item.id}>
                  <td>{item.id}</td>
                  <td className="material-name">{item.material_name}</td>
                  <td className="code-text">{item.hs_code || "-"}</td>
                  <td>{Number(item.current_stock).toLocaleString()}</td>
                  <td>{Number(item.safety_stock).toLocaleString()}</td>
                  <td>{Number(item.daily_usage).toLocaleString()}</td>
                  <td>{item.unit}</td>
                  <td className={remainDays < 10 ? "danger-text" : "safe-text"}>
                    {remainDays.toFixed(1)}일
                  </td>
                  <td>
                    <span className={`inventory-status ${status}`}>
                      {status}
                    </span>
                  </td>
                  <td>
                    <div className="importance-cell">
                      <span>{importance.toFixed(1)}%</span>
                      <div className="importance-bar">
                        <div style={{ width: `${importance}%` }} />
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

        {filteredInventories.length === 0 && (
          <p className="empty-text">등록된 재고 데이터가 없습니다.</p>
        )}
      </div>

      <div className="panel inventory-panel analysis-panel">
        <h3>원자재 비율 / 중요도 분석</h3>

        <div className="importance-summary">
          {inventories.map((item) => {
            const importance = getImportance(item);

            return (
              <div className="summary-item" key={item.id}>
                <div>
                  <strong>{item.material_name}</strong>
                  <p>
                    현재 재고 {Number(item.current_stock).toLocaleString()}{" "}
                    {item.unit}
                  </p>
                </div>
                <span>{importance.toFixed(1)}%</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default Inventory;