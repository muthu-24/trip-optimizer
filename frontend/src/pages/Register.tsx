import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authApi, getErrorMessage, getToken } from "../api";
import "./Auth.css";

function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const navigate = useNavigate();

  useEffect(() => {
    const token = getToken();
    if (token) {
      navigate("/dashboard", { replace: true });
    }
  }, [navigate]);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setValidationError(null);
    setSuccessMessage(null);

    const trimmedName = name.trim();
    const trimmedEmail = email.trim();

    if (!trimmedName || trimmedName.length < 2) {
      setValidationError("Please enter your name (at least 2 characters).");
      return;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!trimmedEmail || !emailRegex.test(trimmedEmail)) {
      setValidationError("Please enter a valid email address.");
      return;
    }
    if (!password || password.length < 8) {
      setValidationError("Password must be at least 8 characters long.");
      return;
    }

    setIsLoading(true);

    try {
      await authApi.register({
        name: trimmedName,
        email: trimmedEmail,
        password,
      });

      setSuccessMessage("Account created successfully! Redirecting you to sign in...");

      setTimeout(() => {
        navigate("/login");
      }, 1400);
    } catch (error: unknown) {
      console.error("Registration failed:", error);
      setErrorMessage(
        getErrorMessage(error, "Registration failed. Please check your information and try again.")
      );
    } finally {
      setIsLoading(false);
    }
  };

  const isFormIncomplete = !name.trim() || !email.trim() || password.length < 8;

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
          <h1 className="auth-title">Create Account</h1>
          <p className="auth-subtitle">Join today to get tailored destination matches and optimized routes</p>
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

        {successMessage && (
          <div className="auth-alert success" role="status">
            <span className="alert-icon">✅</span>
            <span>{successMessage}</span>
          </div>
        )}

        <form onSubmit={handleRegister} className="auth-form" noValidate>
          <div className="auth-field">
            <label className="auth-label" htmlFor="register-name">Full Name</label>
            <input
              id="register-name"
              className="auth-input"
              type="text"
              placeholder="e.g. Jane Doe"
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                if (validationError) setValidationError(null);
              }}
              required
              autoComplete="name"
            />
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="register-email">Email Address</label>
            <input
              id="register-email"
              className="auth-input"
              type="email"
              placeholder="e.g. jane@example.com"
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
              <label className="auth-label" htmlFor="register-password">Password</label>
              <span className="field-requirement-hint">Min. 8 characters</span>
            </div>
            <div className="password-input-wrapper">
              <input
                id="register-password"
                className="auth-input with-toggle"
                type={showPassword ? "text" : "password"}
                placeholder="At least 8 characters"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (validationError) setValidationError(null);
                }}
                required
                autoComplete="new-password"
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
            disabled={isLoading || isFormIncomplete || !!successMessage}
          >
            {isLoading ? (
              <>
                <span className="auth-spinner"></span>
                <span>Creating Account...</span>
              </>
            ) : (
              <span>Create Account →</span>
            )}
          </button>
        </form>

        <footer className="auth-footer">
          <span>Already have an account?</span>
          <Link to="/login">Sign In</Link>
        </footer>
      </div>
    </div>
  );
}

export default Register;