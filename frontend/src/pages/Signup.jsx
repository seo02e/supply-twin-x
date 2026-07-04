import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";
import { signup } from "../services/auth";

function Signup() {
  const navigate = useNavigate();
  const [mode, setMode] = useState("existing"); // "existing" | "new"
  const [companies, setCompanies] = useState([]);

  const [form, setForm] = useState({
    email: "",
    username: "",
    password: "",
    company_id: "",
    business_number: "",
    company_name: "",
    industry_type: "",
  });

  useEffect(() => {
    api
      .get("/companies/")
      .then((res) => setCompanies(res.data))
      .catch(() => setCompanies([]));
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      let companyId = form.company_id;

      if (mode === "new") {
        const companyRes = await api.post("/companies/", {
          company_name: form.company_name,
          business_number: form.business_number || null,
          industry_type: form.industry_type || null,
        });
        companyId = companyRes.data.id;
      }

      await signup({
        email: form.email,
        username: form.username,
        password: form.password,
        company_id: Number(companyId),
        business_number: form.business_number || null,
      });

      alert("회원가입이 완료되었습니다. 로그인해주세요.");
      navigate("/login");
    } catch (err) {
      alert(err.response?.data?.detail || "회원가입에 실패했습니다.");
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
      </section>

      <section className="login-box">
        <h2>회원가입</h2>
        <p>소속 회사를 선택하거나 새로 등록하고 계정을 만드세요.</p>

        <div className="signup-mode-toggle">
          <button
            type="button"
            className={mode === "existing" ? "active" : ""}
            onClick={() => setMode("existing")}
          >
            기존 회사 가입
          </button>
          <button
            type="button"
            className={mode === "new" ? "active" : ""}
            onClick={() => setMode("new")}
          >
            새 회사 등록
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {mode === "existing" ? (
            <select
              name="company_id"
              value={form.company_id}
              onChange={handleChange}
              required
            >
              <option value="">회사 선택</option>
              {companies.map((company) => (
                <option key={company.id} value={company.id}>
                  {company.company_name}
                </option>
              ))}
            </select>
          ) : (
            <>
              <input
                name="company_name"
                placeholder="회사명"
                value={form.company_name}
                onChange={handleChange}
                required
              />
              <input
                name="industry_type"
                placeholder="업종 (선택)"
                value={form.industry_type}
                onChange={handleChange}
              />
            </>
          )}

          <input
            name="business_number"
            placeholder={
              mode === "existing"
                ? "사업자등록번호 (해당 회사 등록 번호와 일치해야 함)"
                : "사업자등록번호 (다른 직원 가입 시 필요, 선택)"
            }
            value={form.business_number}
            onChange={handleChange}
            required={mode === "existing"}
          />

          <input
            name="email"
            type="email"
            placeholder="이메일"
            value={form.email}
            onChange={handleChange}
            required
          />

          <input
            name="username"
            placeholder="이름"
            value={form.username}
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

          <button type="submit">회원가입</button>
        </form>

        <p className="signup-link">
          이미 계정이 있으신가요? <Link to="/login">로그인</Link>
        </p>
      </section>
    </div>
  );
}

export default Signup;
