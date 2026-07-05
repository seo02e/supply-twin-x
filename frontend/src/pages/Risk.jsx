import { useEffect, useState } from "react";
import api from "../services/api";

function Risk() {
  const [inventories, setInventories] = useState([]);
  const [orders, setOrders] = useState([]);
  const [risk, setRisk] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [inventoryRes, orderRes, riskRes] = await Promise.all([
        api.get("/inventory/"),
        api.get("/purchase-orders/"),
        api.get("/risk/summary"),
      ]);

      setInventories(inventoryRes.data);
      setOrders(orderRes.data);
      setRisk(riskRes.data);
    } catch (err) {
      console.error("Risk data fetch failed:", err);
      setError("위험도 데이터를 불러오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const shortageItems = inventories.filter(
    (item) => Number(item.current_stock) < Number(item.safety_stock),
  );

  const delayedOrders = orders.filter((item) => item.status === "DELAYED");

  const getFactor = (name) =>
    risk?.factors?.find((factor) => factor.name === name);

  if (loading) {
    return (
      <div className="risk-page">
        <div className="page-title">
          <h1>Risk Analysis</h1>
          <p>공급망 위험도를 분석하는 중입니다...</p>
        </div>
      </div>
    );
  }

  if (error || !risk) {
    return (
      <div className="risk-page">
        <div className="page-title">
          <h1>Risk Analysis</h1>
          <p>{error || "위험도 데이터가 없습니다."}</p>
        </div>
      </div>
    );
  }

  const totalScore = risk.total_score;
  const level = risk.risk_level;

  return (
    <div className="risk-page">
      <div className="page-title">
        <h1>Risk Analysis</h1>
        <p>ERP 입력 데이터와 공공데이터를 기반으로 AI가 공급망 위험도를 계산합니다.</p>
      </div>

      <div className="grid-4">
        <div className="card danger">
          <p>Total Risk Score</p>
          <h2>{totalScore}</h2>
          <span>{level}</span>

          <div className="risk-score-bar">
            <div style={{ width: `${totalScore}%` }} />
          </div>
        </div>

        {risk.factors.map((factor) => (
          <div className="card" key={factor.name}>
            <p>{factor.name}</p>
            <h2>{factor.score}</h2>
            <span>{factor.reason}</span>
          </div>
        ))}
      </div>

      <div className="grid-2">
        <div className="panel">
          <h3>위험 원인</h3>

          <ul className="risk-list">
            {shortageItems.length > 0 ? (
              shortageItems.map((item) => (
                <li key={item.id}>
                  <strong>{item.material_name}</strong> 재고가 안전재고
                  이하입니다. 현재 재고 {item.current_stock}
                  {item.unit}, 안전재고 {item.safety_stock}
                  {item.unit}
                </li>
              ))
            ) : (
              <li>안전재고 이하 품목이 없습니다.</li>
            )}

            {delayedOrders.length > 0 ? (
              delayedOrders.map((item) => (
                <li key={item.id}>
                  <strong>{item.material_name}</strong> 발주가 지연 상태입니다.
                </li>
              ))
            ) : (
              <li>지연된 발주가 없습니다.</li>
            )}

            {getFactor("가동률") && Number(getFactor("가동률").score) > 0 ? (
              <li>산업단지 가동률 저하가 감지되었습니다.</li>
            ) : (
              <li>가동률은 안정적인 수준입니다.</li>
            )}
          </ul>
        </div>

        <div className="panel">
          <h3>대응 전략</h3>

          <ul className="risk-list">
            <li>안전재고 이하 품목은 즉시 발주 검토가 필요합니다.</li>
            <li>리드타임이 긴 공급업체는 대체 공급처 확보가 필요합니다.</li>
            <li>지연 발주가 발생한 경우 생산계획을 재조정해야 합니다.</li>
            <li>
              가동률 저하가 지속될 경우 원자재 수급과 생산라인 병목을 점검해야
              합니다.
            </li>
          </ul>
        </div>
      </div>

      <div className="panel report">
        <h3>AI 리포트</h3>
        <p>{risk.ai_report}</p>
      </div>
    </div>
  );
}

export default Risk;
