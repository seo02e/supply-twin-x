import Sidebar from "./Sidebar";

function Layout({ children }) {
  const companyName = localStorage.getItem("company_name");
  const userRole = localStorage.getItem("role");

  return (
    <div className="app">
      <Sidebar />

      <main className="main">
        <div className="topbar">
          <div>
            <h2>{companyName || "회사명 없음"}</h2>
            <p>공급망 위험 예측 AI 플랫폼</p>
          </div>

          <div className="user-badge">{userRole || "ROLE 없음"}</div>
        </div>

        {children}
      </main>
    </div>
  );
}

export default Layout;