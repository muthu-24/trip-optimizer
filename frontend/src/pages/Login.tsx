import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/auth/login",
        {
          email,
          password,
        }
      );

      const token = response.data.access_token;

      localStorage.setItem("access_token", token);

      const meResponse = await axios.get(
        "http://127.0.0.1:8000/api/auth/me",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      console.log("Current user:", meResponse.data);

      alert(`Welcome, ${meResponse.data.name}!`);

      navigate("/dashboard");
    } catch (error) {
      console.error("Login failed:", error);

      alert("Login failed!");
    }
  };

  return (
    <div>
      <h1>Login</h1>

      <form onSubmit={handleLogin}>
        <div>
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div>
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button type="submit">
          Login
        </button>
      </form>
    </div>
  );
}

export default Login;