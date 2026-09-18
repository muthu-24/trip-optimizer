import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authApi, getErrorMessage, getToken } from "../api";
import "./Auth.css";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);

  const navigate = useNavigate();

  useEffect(() => {
    const token = getToken();
    if (token) {
      navigate("/dashboard", { replace: true });
    }
  }, [navigate]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setValidationError(null);

    // Basic client validation
    const trimmedEmail = email.trim();
    if (!trimmedEmail) {
      setValidationError("Please enter your email address.");
      return;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(trimmedEmail)) {
      setValidationError("Please enter a valid email address (e.g. wanderer@example.com).");
      return;
    }
    if (!password) {
      setValidationError("Please enter your password.");
      return;
    }

    setIsLoading(true);

    try {
      await authApi.login({
        email: trimmedEmail,
        password,
      });

      try {
        await authApi.getCurrentUser();
      } catch (meError) {
        console.warn("Could not fetch user profile details:", meError);
      }

      navigate("/dashboard");
    } catch (error: unknown) {
      console.error("Login failed:", error);
      setErrorMessage(
        getErrorMessage(error, "Invalid email or password. Please check your credentials.")
      );
    } finally {
      setIsLoading(false);
    }
  };

  const isFormIncomplete = !email.trim() || !password;

  return (
    <div className="auth-page">
      <div className="auth-card">
        <header className="auth-header">
          <div className="auth-logo-badge">
            <svg
              width="28"
              height="28"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="12" r="10"></circle>
              <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon>
            </svg>
          </div>
          <span className="auth-brand-kicker">Trip Optimizer</span>
          <h1 className="auth-title">Welcome Back</h1>
          <p className="auth-subtitle">Sign in to plan and explore your personalized itineraries</p>
        </header>

        {errorMessage && (
          <div className="auth-alert error" role="alert">
            <span className="alert-icon">⚠️</span>
            <span>{errorMessage}</span>
          </div>
        )}

        {validationError && (
          <div className="auth-alert warning" role="alert">
            <span className="alert-icon">ℹ️</span>
            <span>{validationError}</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="auth-form" noValidate>
          <div className="auth-field">
            <label className="auth-label" htmlFor="login-email">Email Address</label>
            <input
              id="login-email"
              className="auth-input"
              type="email"
              placeholder="e.g. wanderer@example.com"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (validationError) setValidationError(null);
              }}
              required
              autoComplete="email"
            />
          </div>

          <div className="auth-field">
            <div className="auth-label-row">
              <label className="auth-label" htmlFor="login-password">Password</label>
            </div>
            <div className="password-input-wrapper">
              <input
                id="login-password"
                className="auth-input with-toggle"
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (validationError) setValidationError(null);
                }}
                required
                autoComplete="current-password"
              />
              <button
                type="button"
                className="password-toggle-btn"
                onClick={() => setShowPassword((prev) => !prev)}
                title={showPassword ? "Hide password" : "Show password"}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                    <line x1="1" y1="1" x2="23" y2="23"></line>
                  </svg>
                ) : (
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                )}
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="auth-submit-btn"
            disabled={isLoading || isFormIncomplete}
          >
            {isLoading ? (
              <>
                <span className="auth-spinner"></span>
                <span>Signing In...</span>
              </>
            ) : (
              <span>Sign In to Dashboard →</span>
            )}
          </button>
        </form>

        <footer className="auth-footer">
          <span>Don't have an account yet?</span>
          <Link to="/register">Create an Account</Link>
        </footer>
      </div>
    </div>
  );
}

export default Login;