import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Register.css";

function Register() {
    const navigate = useNavigate();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [role, setRole] = useState("student");
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const handleRegister = async (e) => {
        e.preventDefault();
        setError("");
        setSuccess("");

        try {
            const response = await fetch(
                "http://127.0.0.1:8000/auth/register",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        email,
                        password,
                        role
                    })
                }
            );

            const data = await response.json();

            if (!response.ok) {
                setError(data.detail || "Registration failed");
                return;
            }

            setSuccess("Registration successful. Please login.");
            setTimeout(() => navigate("/login"), 1500);

        } catch {
            setError("Server error");
        }
    };

    return (
        <div className="register-container">
            <div className="register-card">
                <h2>Create Account</h2>

                {error && <p className="error-text">{error}</p>}
                {success && <p className="success-text">{success}</p>}

                <form onSubmit={handleRegister}>

                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        required
                        onChange={(e) => setEmail(e.target.value)}
                    />

                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        required
                        onChange={(e) => setPassword(e.target.value)}
                    />

                    <select
                        value={role}
                        onChange={(e) => setRole(e.target.value)}
                    >
                        <option value="student">Student</option>
                        <option value="recruiter">Recruiter</option>
                    </select>

                    <button type="submit">
                        Register
                    </button>

                </form>
            </div>
        </div>
    );

}

export default Register;
