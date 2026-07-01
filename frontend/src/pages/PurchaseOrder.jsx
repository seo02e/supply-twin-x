import { useEffect, useState } from "react";
import api from "../services/api";

function PurchaseOrder() {
  const [orders, setOrders] = useState([]);

  const [form, setForm] = useState({
    company_id: 1,
    supplier_id: 1,
    material_name: "",
    quantity: "",
    order_date: "",
    expected_arrival_date: "",
    status: "ORDERED",
  });

  const fetchOrders = async () => {
    const res = await api.get("/purchase-orders/");
    setOrders(res.data);
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    await api.post("/purchase-orders/", {
      ...form,
      company_id: Number(form.company_id),
      supplier_id: Number(form.supplier_id),
      quantity: Number(form.quantity),
    });

    setForm({
      company_id: 1,
      supplier_id: 1,
      material_name: "",
      quantity: "",
      order_date: "",
      expected_arrival_date: "",
      status: "ORDERED",
    });

    fetchOrders();
  };

  const handleDelete = async (id) => {
    await api.delete(`/purchase-orders/${id}`);
    fetchOrders();
  };

  return (
    <div>
      <div className="page-title">
        <h1>Purchase Orders</h1>
        <p>발주 데이터를 등록하고 납기 지연 위험 분석에 활용합니다.</p>
      </div>

      <div className="panel">
        <h3>발주 등록</h3>

        <form className="form-grid" onSubmit={handleSubmit}>
          <input
            name="supplier_id"
            type="number"
            placeholder="공급업체 ID"
            value={form.supplier_id}
            onChange={handleChange}
            required
          />

          <input
            name="material_name"
            placeholder="원자재명"
            value={form.material_name}
            onChange={handleChange}
            required
          />

          <input
            name="quantity"
            type="number"
            placeholder="발주 수량"
            value={form.quantity}
            onChange={handleChange}
            required
          />

          <input
            name="order_date"
            type="date"
            value={form.order_date}
            onChange={handleChange}
            required
          />

          <input
            name="expected_arrival_date"
            type="date"
            value={form.expected_arrival_date}
            onChange={handleChange}
            required
          />

          <select name="status" value={form.status} onChange={handleChange}>
            <option value="ORDERED">ORDERED</option>
            <option value="SHIPPED">SHIPPED</option>
            <option value="DELAYED">DELAYED</option>
            <option value="COMPLETED">COMPLETED</option>
          </select>

          <button type="submit">등록</button>
        </form>
      </div>

      <div className="panel table-panel">
        <h3>발주 목록</h3>

        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>공급업체 ID</th>
              <th>원자재</th>
              <th>수량</th>
              <th>발주일</th>
              <th>입고예정일</th>
              <th>상태</th>
              <th>관리</th>
            </tr>
          </thead>

          <tbody>
            {orders.map((item) => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.supplier_id}</td>
                <td>{item.material_name}</td>
                <td>{item.quantity}</td>
                <td>{item.order_date}</td>
                <td>{item.expected_arrival_date}</td>
                <td>
                  <span className={`status ${item.status.toLowerCase()}`}>
                    {item.status}
                  </span>
                </td>
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

        {orders.length === 0 && (
          <p className="empty-text">등록된 발주 데이터가 없습니다.</p>
        )}
      </div>
    </div>
  );
}

export default PurchaseOrder;
