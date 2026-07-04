import { useEffect, useState } from "react";
import api from "../services/api";

function Risk() {
  const [inventories, setInventories] = useState([]);
  const [orders, setOrders] = useState([]);
  const [productions, setProductions] = useState([]);

  const fetchData = async () => {
    const [inventoryRes, orderRes, productionRes] = await Promise.all([
      api.get("/inventory/"),
      api.get("/purchase-orders/"),
      api.get("/productions/"),
    ]);

    setInventories(inventoryRes.data);
    setOrders(orderRes.data);
    setProductions(productionRes.data);
  };

  useEffect(() => {
    fetchData();
  }, []);

  const shortageItems = inventories.filter(
    (item) => Number(item.current_stock) < Number(item.safety_stock),
  );

  const delayedOrders = orders.filter((item) => item.status === "DELAYED");

  const avgOperationRate =
    productions.length > 0
      ? productions.reduce(
          (sum, item) => sum + Number(item.operation_rate),
          0,
        ) / productions.length
      : 0;

  const inventoryScore = shortageItems.length * 30;
  const orderScore = delayedOrders.length * 20;
  const operationScore = avgOperationRate > 0 && avgOperationRate < 80 ? 20 : 0;

  const totalScore = Math.min(
    100,
    inventoryScore + orderScore + operationScore,
  );

  const level = totalScore >= 70 ? "HIGH" : totalScore >= 40 ? "MEDIUM" : "LOW";

  return (
  <div className="risk-page">
      <div className="page-title">
        <h1>Risk Analysis</h1>
        <p>ERP 입력 데이터를 기반으로 공급망 위험도를 계산합니다.</p>
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

        <div className="card">
          <p>재고 위험</p>
          <h2>{inventoryScore}</h2>
          <span>{shortageItems.length} items below safety stock</span>
        </div>

        <div className="card">
          <p>발주 위험</p>
          <h2>{orderScore}</h2>
          <span>{delayedOrders.length} delayed orders</span>
        </div>

        <div className="card">
          <p>가동률 위험</p>
          <h2>{operationScore}</h2>
          <span>Avg. operation rate {avgOperationRate.toFixed(1)}%</span>
        </div>
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

            {operationScore > 0 ? (
              <li>평균 가동률이 80% 미만으로 하락했습니다.</li>
            ) : (
              <li>평균 가동률은 안정적인 수준입니다.</li>
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
        <h3>AI 리포트 미리보기</h3>
        <p>
          현재 공급망 위험도는 <strong>{level}</strong> 단계입니다. 총 위험
          점수는 <strong>{totalScore}점</strong>이며, 주요 위험 요인은 재고
          부족, 발주 지연, 생산 가동률 저하 여부를 기준으로 산정되었습니다. 이후
          OpenAI API를 연결하면 이 영역에 원인 분석과 대응 전략이 자동
          생성됩니다.
        </p>
      </div>
    </div>
  );
}

export default Risk;
