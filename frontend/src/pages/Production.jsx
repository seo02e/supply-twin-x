import { useEffect, useState } from "react";
import api from "../services/api";

function Production() {
  const [productions, setProductions] = useState([]);

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

  const handleDelete = async (id) => {
    await api.delete(`/productions/${id}`);
    fetchProductions();
  };

  return (
    <div>
      <div className="page-title">
        <h1>Productions</h1>
        <p>
          생산량과 가동률 데이터를 등록하고 생산 중단 위험 분석에 활용합니다.
        </p>
      </div>

      <div className="panel">
        <h3>생산 데이터 등록</h3>

        <form className="form-grid" onSubmit={handleSubmit}>
          <input
            name="product_name"
            placeholder="제품명 예: EV Battery Module"
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

          <button type="submit">등록</button>
        </form>
      </div>

      <div className="panel table-panel">
        <h3>생산 데이터 목록</h3>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>제품명</th>
              <th>생산량</th>
              <th>가동률</th>
              <th>생산일자</th>
              <th>관리</th>
            </tr>
          </thead>

          <tbody>
            {productions.map((item) => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.product_name}</td>
                <td>{item.production_quantity}</td>
                <td>{item.operation_rate}%</td>
                <td>{item.production_date}</td>
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

        {productions.length === 0 && (
          <p className="empty-text">등록된 생산 데이터가 없습니다.</p>
        )}
      </div>
    </div>
  );
}

export default Production;
