import { useEffect, useMemo, useState } from "react";
import api from "../services/api";

function PurchaseOrder() {
  const [orders, setOrders] = useState([]);
  const [keyword, setKeyword] = useState("");

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

  const filteredOrders = useMemo(() => {
    return orders.filter((item) => {
      const text = `${item.material_name} ${item.status} ${item.supplier_id}`.toLowerCase();
      return text.includes(keyword.toLowerCase());
    });
  }, [orders, keyword]);

  const getDaysLeft = (date) => {
    const today = new Date();
    const arrival = new Date(date);
    today.setHours(0, 0, 0, 0);
    arrival.setHours(0, 0, 0, 0);
    return Math.ceil((arrival - today) / (1000 * 60 * 60 * 24));
  };

  const getDeliveryRisk = (item) => {
    const daysLeft = getDaysLeft(item.expected_arrival_date);

    if (item.status === "COMPLETED") return "완료";
    if (item.status === "DELAYED") return "지연";
    if (daysLeft < 0) return "지연";
    if (daysLeft <= 7) return "임박";
    return "정상";
  };

  const getRiskScore = (item) => {
    const daysLeft = getDaysLeft(item.expected_arrival_date);

    if (item.status === "COMPLETED") return 0;
    if (item.status === "DELAYED" || daysLeft < 0) return 100;
    if (daysLeft <= 7) return 70;
    if (daysLeft <= 14) return 40;
    return 15;
  };

  const totalQuantity = useMemo(() => {
    return orders.reduce((sum, item) => sum + Number(item.quantity || 0), 0);
  }, [orders]);

  const delayedCount = orders.filter((item) => getDeliveryRisk(item) === "지연").length;
  const urgentCount = orders.filter((item) => getDeliveryRisk(item) === "임박").length;

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

  const handleEdit = (item) => {
    setForm({
      company_id: item.company_id,
      supplier_id: item.supplier_id,
      material_name: item.material_name,
      quantity: item.quantity,
      order_date: item.order_date,
      expected_arrival_date: item.expected_arrival_date,
      status: item.status,
    });
  };

  const handleDelete = async (id) => {
    await api.delete(`/purchase-orders/${id}`);
    fetchOrders();
  };

  return (
    <div className="po-page">
      <div className="page-title">
        <h1>Purchase Orders</h1>
        <p>발주 데이터를 등록하고 납기 지연 위험 분석에 활용합니다.</p>
      </div>

      <div className="po-kpi-grid">
        <div className="po-kpi-card">
          <p>총 발주 건수</p>
          <h2>{orders.length}건</h2>
        </div>
        <div className="po-kpi-card danger">
          <p>지연 발주</p>
          <h2>{delayedCount}건</h2>
        </div>
        <div className="po-kpi-card warning">
          <p>입고 임박</p>
          <h2>{urgentCount}건</h2>
        </div>
        <div className="po-kpi-card">
          <p>총 발주 수량</p>
          <h2>{totalQuantity.toLocaleString()}</h2>
        </div>
      </div>

      <div className="panel po-panel">
        <h3>발주 등록</h3>

        <form className="po-form" onSubmit={handleSubmit}>
          <input name="supplier_id" type="number" placeholder="공급업체 ID" value={form.supplier_id} onChange={handleChange} required />
          <input name="material_name" placeholder="원자재명" value={form.material_name} onChange={handleChange} required />
          <input name="quantity" type="number" placeholder="발주 수량" value={form.quantity} onChange={handleChange} required />
          <input name="order_date" type="date" value={form.order_date} onChange={handleChange} required />
          <input name="expected_arrival_date" type="date" value={form.expected_arrival_date} onChange={handleChange} required />

          <select name="status" value={form.status} onChange={handleChange}>
            <option value="ORDERED">ORDERED</option>
            <option value="SHIPPED">SHIPPED</option>
            <option value="DELAYED">DELAYED</option>
            <option value="COMPLETED">COMPLETED</option>
          </select>

          <button type="submit">등록 / 수정</button>
        </form>
      </div>

      <div className="panel table-panel po-panel">
        <div className="panel-header">
          <h3>발주 목록</h3>
          <input
            className="search-input"
            placeholder="원자재, 상태, 공급업체 ID 검색..."
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
          />
        </div>

        <table className="po-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>공급업체 ID</th>
              <th>원자재</th>
              <th>수량</th>
              <th>발주일</th>
              <th>입고예정일</th>
              <th>남은 입고일수</th>
              <th>상태</th>
              <th>납기 리스크</th>
              <th>리스크 지수</th>
              <th>관리</th>
            </tr>
          </thead>

          <tbody>
            {filteredOrders.map((item) => {
              const daysLeft = getDaysLeft(item.expected_arrival_date);
              const deliveryRisk = getDeliveryRisk(item);
              const score = getRiskScore(item);

              return (
                <tr key={item.id}>
                  <td>{item.id}</td>
                  <td>{item.supplier_id}</td>
                  <td className="material-name">{item.material_name}</td>
                  <td>{Number(item.quantity).toLocaleString()}</td>
                  <td>{item.order_date}</td>
                  <td>{item.expected_arrival_date}</td>
                  <td className={daysLeft < 0 ? "po-danger-text" : daysLeft <= 7 ? "po-warning-text" : "po-safe-text"}>
                    {daysLeft < 0 ? `${Math.abs(daysLeft)}일 지연` : `${daysLeft}일 남음`}
                  </td>
                  <td>
                    <span className={`status ${item.status.toLowerCase()}`}>
                      {item.status}
                    </span>
                  </td>
                  <td>
                    <span className={`po-risk-status ${deliveryRisk}`}>
                      {deliveryRisk}
                    </span>
                  </td>
                  <td>
                    <div className="po-risk-cell">
                      <span>{score}점</span>
                      <div className="po-risk-bar">
                        <div style={{ width: `${score}%` }} />
                      </div>
                    </div>
                  </td>
                  <td className="action-cell">
                    <button className="edit-btn" onClick={() => handleEdit(item)}>
                      수정
                    </button>
                    <button className="delete-btn" onClick={() => handleDelete(item.id)}>
                      삭제
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {filteredOrders.length === 0 && (
          <p className="empty-text">등록된 발주 데이터가 없습니다.</p>
        )}
      </div>
    </div>
  );
}

export default PurchaseOrder;