import { useEffect, useState } from "react";
import api from "../services/api";

function Supplier() {
  const [suppliers, setSuppliers] = useState([]);

  const [form, setForm] = useState({
    company_id: 1,
    supplier_name: "",
    country: "",
    material_name: "",
    lead_time_days: "",
  });

  const fetchSuppliers = async () => {
    const res = await api.get("/suppliers/");
    setSuppliers(res.data);
  };

  useEffect(() => {
    fetchSuppliers();
  }, []);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    await api.post("/suppliers/", {
      ...form,
      company_id: Number(form.company_id),
      lead_time_days: Number(form.lead_time_days),
    });

    setForm({
      company_id: 1,
      supplier_name: "",
      country: "",
      material_name: "",
      lead_time_days: "",
    });

    fetchSuppliers();
  };

  const handleDelete = async (id) => {
    await api.delete(`/suppliers/${id}`);
    fetchSuppliers();
  };

  return (
    <div>
      <div className="page-title">
        <h1>Suppliers</h1>
        <p>공급업체를 등록하고 공급망 위험 분석에 활용합니다.</p>
      </div>

      <div className="panel">
        <h3>공급업체 등록</h3>

        <form className="form-grid" onSubmit={handleSubmit}>
          <input
            name="supplier_name"
            placeholder="공급업체명"
            value={form.supplier_name}
            onChange={handleChange}
            required
          />

          <input
            name="country"
            placeholder="국가"
            value={form.country}
            onChange={handleChange}
            required
          />

          <input
            name="material_name"
            placeholder="원자재"
            value={form.material_name}
            onChange={handleChange}
            required
          />

          <input
            name="lead_time_days"
            type="number"
            placeholder="Lead Time"
            value={form.lead_time_days}
            onChange={handleChange}
            required
          />

          <button type="submit">등록</button>
        </form>
      </div>

      <div className="panel table-panel">
        <h3>공급업체 목록</h3>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>공급업체</th>
              <th>국가</th>
              <th>원자재</th>
              <th>Lead Time</th>
              <th>관리</th>
            </tr>
          </thead>

          <tbody>
            {suppliers.map((item) => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.supplier_name}</td>
                <td>{item.country}</td>
                <td>{item.material_name}</td>
                <td>{item.lead_time_days}일</td>
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

        {suppliers.length === 0 && (
          <p className="empty-text">등록된 공급업체가 없습니다.</p>
        )}
      </div>
    </div>
  );
}

export default Supplier;
