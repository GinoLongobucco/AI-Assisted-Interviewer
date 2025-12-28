"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { adminLogin } from "@/services/AdminService";

export default function AdminLoginPage() {
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            await adminLogin(email, password);
            // Redirect to dashboard on success
            router.push("/admin/dashboard");
        } catch (err) {
            setError(err.message || "Login failed");
            setLoading(false);
        }
    };

    return (
        <div className="container py-5">
            <div className="row justify-content-center">
                <div className="col-md-5 col-lg-4">
                    <div className="card shadow">
                        <div className="card-body p-4">
                            <div className="text-center mb-4">
                                <h2>Admin Login</h2>
                                <p className="text-muted small">AI Interview Dashboard</p>
                            </div>

                            {error && (
                                <div className="alert alert-danger" role="alert">
                                    {error}
                                </div>
                            )}

                            <form onSubmit={handleSubmit}>
                                <div className="mb-3">
                                    <label htmlFor="email" className="form-label">
                                        Email
                                    </label>
                                    <input
                                        type="email"
                                        className="form-control"
                                        id="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                        disabled={loading}
                                        placeholder="admin@example.com"
                                    />
                                </div>

                                <div className="mb-4">
                                    <label htmlFor="password" className="form-label">
                                        Password
                                    </label>
                                    <input
                                        type="password"
                                        className="form-control"
                                        id="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                        disabled={loading}
                                        placeholder="Enter your password"
                                    />
                                </div>

                                <button
                                    type="submit"
                                    className="btn btn-primary w-100"
                                    disabled={loading}
                                >
                                    {loading ? "Logging in..." : "Login"}
                                </button>
                            </form>

                            <div className="mt-4 text-center">
                                <a href="/" className="text-muted small">
                                    ← Back to Home
                                </a>
                            </div>

                            <div className="mt-4 p-3 bg-light rounded">
                                <p className="small mb-1"><strong>Default Credentials:</strong></p>
                                <p className="small mb-0">Email: admin@example.com</p>
                                <p className="small mb-0">Password: Admin@123456</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
