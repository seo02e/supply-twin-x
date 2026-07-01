import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";

import Dashboard from "./pages/Dashboard";
import Inventory from "./pages/Inventory";
import Supplier from "./pages/Supplier";
import PurchaseOrder from "./pages/PurchaseOrder";
import Production from "./pages/Production";
import Risk from "./pages/Risk";
import Login from "./pages/Login";

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("access_token");

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/inventory"
          element={
            <ProtectedRoute>
              <Layout>
                <Inventory />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/suppliers"
          element={
            <ProtectedRoute>
              <Layout>
                <Supplier />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/purchase-orders"
          element={
            <ProtectedRoute>
              <Layout>
                <PurchaseOrder />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/productions"
          element={
            <ProtectedRoute>
              <Layout>
                <Production />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/risk"
          element={
            <ProtectedRoute>
              <Layout>
                <Risk />
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
