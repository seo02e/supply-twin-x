import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../services/auth";

function Login() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const res = await login(form);

      localStorage.setItem("access_token", res.data.access_token);
      localStorage.setItem("company_id", res.data.company_id);
      localStorage.setItem("company_name", res.data.company_name);
      localStorage.setItem("role", res.data.role);
      localStorage.setItem("username", res.data.username);

      navigate("/");
    } catch (err) {
      alert("로그인에 실패했습니다.");
      console.log(err);
    }
  };

  return (
    <div className="login-page">
      <section className="login-hero">
        <div className="hero-badge">Supply Chain Digital Twin</div>
        <h1>Supply Twin-X</h1>
        <p>
          기업 ERP 데이터와 공공데이터를 결합해 원자재 수급, 발주 지연, 생산
          가동률 위험을 AI가 분석하는 공급망 위험 예측 플랫폼입니다.
        </p>

        <div className="hero-features">
          <div>공공데이터 기반 수출입 분석</div>
          <div>ERP 재고·발주·생산 통합 관리</div>
          <div>AI 위험도 예측 및 대응 리포트</div>
        </div>
      </section>

      <section className="login-box">
        <h2>로그인</h2>
        <p>기업 계정으로 Supply Twin-X에 접속하세요.</p>

        <form onSubmit={handleLogin}>
          <input
            name="email"
            type="email"
            placeholder="이메일"
            value={form.email}
            onChange={handleChange}
            required
          />

          <input
            name="password"
            type="password"
            placeholder="비밀번호"
            value={form.password}
            onChange={handleChange}
            required
          />

          <button type="submit">Dashboard 접속</button>
        </form>

        <p className="signup-link">
          계정이 없으신가요? <Link to="/signup">회원가입</Link>
        </p>
      </section>
    </div>
  );
}

export default Login;