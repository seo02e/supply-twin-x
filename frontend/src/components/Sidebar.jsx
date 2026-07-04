import { NavLink, useNavigate } from "react-router-dom";

function Sidebar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("company_id");
    localStorage.removeItem("company_name");
    localStorage.removeItem("username");
    localStorage.removeItem("role");

    navigate("/login");
  };

  return (
    <aside className="sidebar">
      <h1>STX</h1>
      <p className="logo-text">Supply Twin-X</p>

      <nav>
        <NavLink to="/">Dashboard</NavLink>
        <NavLink to="/inventory">Inventory</NavLink>
        <NavLink to="/suppliers">Suppliers</NavLink>
        <NavLink to="/purchase-orders">Purchase Orders</NavLink>
        <NavLink to="/productions">Productions</NavLink>
        <NavLink to="/risk">Risk Analysis</NavLink>
      </nav>

      <button className="logout-btn" onClick={handleLogout}>
        로그아웃
      </button>
    </aside>
  );
}

export default Sidebar;