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
  PieChart,
  Pie,
  Cell,
} from "recharts";

function Dashboard() {
  const [inventories, setInventories] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [productions, setProductions] = useState([]);
  const [exchange, setExchange] = useState(null);

  const fetchDashboardData = async () => {
  const companyId = localStorage.getItem("company_id");

  try {
    const [inventoryRes, supplierRes, orderRes, productionRes, exchangeRes] =
      await Promise.all([
        api.get(`/inventory/?company_id=${companyId}`),
        api.get(`/suppliers/?company_id=${companyId}`),
        api.get(`/purchase-orders/?company_id=${companyId}`),
        api.get(`/productions/?company_id=${companyId}`),
        api.get("/exchange/usd").catch(() => ({ data: null })),
      ]);

      setInventories(inventoryRes.data);
      setSuppliers(supplierRes.data);
      setOrders(orderRes.data);
      setProductions(productionRes.data);
      setExchange(exchangeRes.data);
    } catch (error) {
      console.error("Dashboard data fetch failed:", error);
    }
  };

  useEffect(() => {
  const token = localStorage.getItem("access_token");
  if (!token) return;

  fetchDashboardData();
}, []);

  const shortageItems = inventories.filter(
    (item) => Number(item.current_stock) < Number(item.safety_stock)
  );

  const delayedOrders = orders.filter((item) => item.status === "DELAYED");

  const avgOperationRate =
    productions.length > 0
      ? (
          productions.reduce((sum, item) => sum + Number(item.operation_rate), 0) /
          productions.length
        ).toFixed(1)
      : 0;

  const inventoryRisk = Math.min(35, shortageItems.length * 20);
  const orderRisk = Math.min(20, delayedOrders.length * 20);
  const operationRisk = avgOperationRate < 80 ? 20 : 0;
  const exchangeRisk = exchange ? 15 : 0;
  const oilRisk = 25;

  const riskScore = Math.min(
    100,
    inventoryRisk + orderRisk + operationRisk + exchangeRisk + oilRisk
  );

  const riskLevel =
    riskScore >= 70 ? "HIGH RISK" : riskScore >= 40 ? "MEDIUM RISK" : "LOW RISK";

  const priceData = [
    { month: "1월", dubai: 82, wti: 78, exchange: 1320 },
    { month: "2월", dubai: 86, wti: 81, exchange: 1360 },
    { month: "3월", dubai: 91, wti: 84, exchange: 1410 },
    { month: "4월", dubai: 95, wti: 88, exchange: 1480 },
    { month: "5월", dubai: 101, wti: 92, exchange: exchange?.base_rate || 1554 },
  ];

  const riskData = [
    { name: "원유 가격", score: oilRisk },
    { name: "환율", score: exchangeRisk },
    { name: "재고 부족", score: inventoryRisk },
    { name: "발주 지연", score: orderRisk },
    { name: "가동률", score: operationRisk },
  ];

  const pieData = riskData.filter((item) => item.score > 0);

  return (
    <div className="dark-dashboard">
      <div className="dash-header">
        <div>
          <h1>Dashboard <span>Real-time</span></h1>
          <p>공급망 전체를 연결하여 위험을 예측하고 대응 전략을 제시합니다.</p>
        </div>
        <div className="date-pill">2026.07.03</div>
      </div>

      <div className="kpi-grid">
        <div className="kpi-card risk">
          <p>Global Risk Score</p>
          <h2>{riskScore}<small>/100</small></h2>
          <strong>{riskLevel}</strong>
        </div>

        <div className="kpi-card">
          <p>Dubai Oil Price</p>
          <h2>87.45<small>$/bbl</small></h2>
          <strong className="up">▲ 8.2% vs 7일 전</strong>
        </div>

        <div className="kpi-card">
          <p>USD / KRW</p>
          <h2>{exchange ? Number(exchange.base_rate).toLocaleString() : "-"}</h2>
          <strong className="up">▲ API 연동 완료</strong>
        </div>

        <div className="kpi-card">
          <p>Factory Operation</p>
          <h2>{avgOperationRate}<small>%</small></h2>
          <strong className="down">▼ 평균 가동률</strong>
        </div>
      </div>

      <div className="dash-grid">
        <section className="dark-panel network">
          <div className="panel-title">
            <h3>Supply Chain Network</h3>
            <button>전체 네트워크 보기</button>
          </div>

          <div className="network-flow">
            <div className="node green">
              <b>Saudi Aramco</b>
              <span>Saudi Arabia</span>
            </div>
            <div className="line warn"></div>
            <div className="node blue">
              <b>Busan Port</b>
              <span>South Korea</span>
            </div>
            <div className="line danger"></div>
            <div className="node red">
              <b>Supply Twin-X</b>
              <span>Our Factory</span>
            </div>
            <div className="line danger"></div>
            <div className="node red">
              <b>Production Line</b>
              <span>{avgOperationRate}%</span>
            </div>
          </div>

          <div className="legend">
            <span className="ok">정상</span>
            <span className="warning">주의</span>
            <span className="bad">위험</span>
          </div>
        </section>

        <section className="dark-panel ai">
          <h3>AI Analysis Report</h3>
          <h2>현재 공급망 위험도는 {riskLevel} 단계입니다.</h2>

          <ul>
            <li>원유 가격 상승 위험 반영</li>
            <li>USD/KRW 환율 {exchange ? Number(exchange.base_rate).toLocaleString() : "-"}원 반영</li>
            <li>안전재고 이하 품목 {shortageItems.length}개</li>
            <li>지연 발주 {delayedOrders.length}건 발생</li>
          </ul>

          <div className="recommend">
            <b>AI 권장 대응 전략</b>
            <p>대체 공급처 확보, 안전재고 보충, 생산계획 조정이 필요합니다.</p>
          </div>
        </section>

        <section className="dark-panel">
          <h3>Commodity Price Trend</h3>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={priceData}>
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="dubai" strokeWidth={3} />
              <Line type="monotone" dataKey="wti" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </section>

        <section className="dark-panel">
          <h3>Risk Factor Breakdown</h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={pieData} dataKey="score" nameKey="name" innerRadius={60} outerRadius={95}>
                {pieData.map((_, index) => (
                  <Cell key={index} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </section>

        <section className="dark-panel wide">
          <h3>Risk Factor Score</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={riskData}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="score" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </section>
      </div>
    </div>
  );
}

export default Dashboard;