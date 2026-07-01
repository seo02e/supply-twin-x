import { useEffect, useState } from "react";
import api from "../services/api";

function Inventory() {
  const [inventories, setInventories] = useState([]);
  const [form, setForm] = useState({
    company_id: 1,
    material_name: "",
    hs_code: "",
    current_stock: "",
    safety_stock: "",
    daily_usage: "",
    unit: "kg",
  });

  const fetchInventories = async () => {
    const res = await api.get("/inventory/");
    setInventories(res.data);
  };

  useEffect(() => {
    fetchInventories();
  }, []);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    await api.post("/inventory/", {
      ...form,
      company_id: Number(form.company_id),
      current_stock: Number(form.current_stock),
      safety_stock: Number(form.safety_stock),
      daily_usage: Number(form.daily_usage),
    });

    setForm({
      company_id: 1,
      material_name: "",
      hs_code: "",
      current_stock: "",
      safety_stock: "",
      daily_usage: "",
      unit: "kg",
    });

    fetchInventories();
  };

  const handleDelete = async (id) => {
    await api.delete(`/inventory/${id}`);
    fetchInventories();
  };

  return (
    <div>
      <div className="page-title">
        <h1>Inventory</h1>
        <p>재고 데이터를 등록하고 공급망 위험 분석에 활용합니다.</p>
      </div>

      <div className="panel">
        <h3>재고 등록</h3>

        <form className="form-grid" onSubmit={handleSubmit}>
          <input
            name="material_name"
            placeholder="원자재명 예: Lithium"
            value={form.material_name}
            onChange={handleChange}
            required
          />
          <input
            name="hs_code"
            placeholder="HS Code 예: 283691"
            value={form.hs_code}
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

          <button type="submit">재고 등록</button>
        </form>
      </div>

      <div className="panel table-panel">
        <h3>재고 목록</h3>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>원자재명</th>
              <th>HS Code</th>
              <th>현재 재고</th>
              <th>안전 재고</th>
              <th>일일 사용량</th>
              <th>단위</th>
              <th>관리</th>
            </tr>
          </thead>
          <tbody>
            {inventories.map((item) => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.material_name}</td>
                <td>{item.hs_code}</td>
                <td>{item.current_stock}</td>
                <td>{item.safety_stock}</td>
                <td>{item.daily_usage}</td>
                <td>{item.unit}</td>
                <td>
                  <button
                    className="delete-btn"
                    onClick={() => handleDelete(item.id)}
                  >
                    삭제
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {inventories.length === 0 && (
          <p className="empty-text">등록된 재고 데이터가 없습니다.</p>
        )}
      </div>
    </div>
  );
}

export default Inventory;
