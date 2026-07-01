import { useEffect, useState } from "react";
import api from "../services/api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

function Dashboard() {
  const [inventories, setInventories] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [productions, setProductions] = useState([]);

  const fetchDashboardData = async () => {
    const [inventoryRes, supplierRes, orderRes, productionRes] =
      await Promise.all([
        api.get("/inventory/"),
        api.get("/suppliers/"),
        api.get("/purchase-orders/"),
        api.get("/productions/"),
      ]);

    setInventories(inventoryRes.data);
    setSuppliers(supplierRes.data);
    setOrders(orderRes.data);
    setProductions(productionRes.data);
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const shortageItems = inventories.filter(
    (item) => Number(item.current_stock) < Number(item.safety_stock),
  );

  const delayedOrders = orders.filter((item) => item.status === "DELAYED");

  const avgOperationRate =
    productions.length > 0
      ? (
          productions.reduce(
            (sum, item) => sum + Number(item.operation_rate),
            0,
          ) / productions.length
        ).toFixed(1)
      : 0;

  const riskScore = Math.min(
    100,
    shortageItems.length * 30 +
      delayedOrders.length * 20 +
      (avgOperationRate < 80 ? 20 : 0),
  );

  const riskLevel =
    riskScore >= 70 ? "HIGH" : riskScore >= 40 ? "MEDIUM" : "LOW";

  const priceData = [
    { month: "1월", price: 100 },
    { month: "2월", price: 115 },
    { month: "3월", price: 132 },
    { month: "4월", price: 148 },
    { month: "5월", price: 171 },
  ];

  const riskData = [
    { name: "재고", score: shortageItems.length * 30 },
    { name: "발주", score: delayedOrders.length * 20 },
    { name: "가동률", score: avgOperationRate < 80 ? 20 : 0 },
  ];

  return (
    <div>
      <div className="page-title">
        <h1>Dashboard</h1>
        <p>ERP 데이터와 공공데이터를 결합해 공급망 위험을 분석합니다.</p>
      </div>

      <div className="grid-4">
        <div className="card danger">
          <p>Risk Score</p>
          <h2>{riskScore}</h2>
          <span>{riskLevel}</span>
        </div>

        <div className="card">
          <p>현재 재고 품목</p>
          <h2>{inventories.length}</h2>
          <span>Inventory Items</span>
        </div>

        <div className="card">
          <p>등록 공급처</p>
          <h2>{suppliers.length}</h2>
          <span>Suppliers</span>
        </div>

        <div className="card">
          <p>진행 발주</p>
          <h2>{orders.length}</h2>
          <span>Purchase Orders</span>
        </div>
      </div>

      <div className="grid-2">
        <div className="panel">
          <h3>원자재 가격 추이</h3>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={priceData}>
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="price" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="panel">
          <h3>위험 요인 점수</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={riskData}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="score" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="panel report">
        <h3>AI Risk Report</h3>
        <p>
          현재 등록된 재고 품목은 {inventories.length}개이며, 안전재고 이하
          품목은 {shortageItems.length}개입니다. 지연 발주는{" "}
          {delayedOrders.length}건이고, 평균 가동률은 {avgOperationRate}%입니다.
          현재 위험도는 {riskLevel} 단계로 판단됩니다.
        </p>
      </div>
    </div>
  );
}

export default Dashboard;
