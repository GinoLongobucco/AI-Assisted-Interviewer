"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
    getInterviews,
    getAdminConfig,
    updateAdminConfig,
    isAuthenticated,
    logout,
    getAdminEmail,
} from "@/services/AdminService";

export default function AdminDashboard() {
    const router = useRouter();

    // Auth state
    const [adminEmail, setAdminEmail] = useState("");

    // Interviews state
    const [interviews, setInterviews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [filters, setFilters] = useState({ role: "", email: "" });

    // Config state
    const [showConfig, setShowConfig] = useState(false);
    const [config, setConfig] = useState({
        MAX_QUESTIONS: "10",
        QUESTION_TIMEOUT_SECONDS: "120",
    });
    const [configLoading, setConfigLoading] = useState(false);
    const [configMessage, setConfigMessage] = useState("");

    // Check authentication on mount
    useEffect(() => {
        if (!isAuthenticated()) {
            router.push("/admin/login");
            return;
        }
        setAdminEmail(getAdminEmail() || "");
        loadInterviews();
        loadConfig();
    }, []);

    const loadConfig = async () => {
        try {
            const data = await getAdminConfig();
            setConfig(data);
        } catch (error) {
            console.error("Error loading config:", error);
        }
    };

    const loadInterviews = async (currentPage = page) => {
        try {
            setLoading(true);
            const data = await getInterviews(currentPage, 20, filters);
            setInterviews(data.interviews);
            setTotalPages(data.pagination.pages);
            setPage(currentPage);
        } catch (error) {
            console.error("Error loading interviews:", error);
            if (error.message.includes("Authentication")) {
                router.push("/admin/login");
            }
        } finally {
            setLoading(false);
        }
    };

    const handleConfigSubmit = async (e) => {
        e.preventDefault();
        setConfigLoading(true);
        setConfigMessage("");

        try {
            await updateAdminConfig({
                MAX_QUESTIONS: parseInt(config.MAX_QUESTIONS),
                QUESTION_TIMEOUT_SECONDS: parseInt(config.QUESTION_TIMEOUT_SECONDS),
            });
            setConfigMessage("Configuration updated successfully!");
            setTimeout(() => setConfigMessage(""), 3000);
        } catch (error) {
            setConfigMessage(`Error: ${error.message}`);
        } finally {
            setConfigLoading(false);
        }
    };

    const handleLogout = () => {
        logout();
        router.push("/admin/login");
    };

    const handleFilterChange = (key, value) => {
        setFilters({ ...filters, [key]: value });
    };

    const applyFilters = () => {
        loadInterviews(1);
    };

    const clearFilters = () => {
        setFilters({ role: "", email: "" });
        setTimeout(() => loadInterviews(1), 100);
    };

    const formatDate = (dateString) => {
        if (!dateString) return "N/A";
        const date = new Date(dateString);
        return date.toLocaleString();
    };

    const viewInterview = (interviewId) => {
        router.push(`/admin/interview/${interviewId}`);
    };

    return (
        <div className="container-fluid py-4">
            {/* Header */}
            <div className="row mb-4">
                <div className="col">
                    <div className="d-flex justify-content-between align-items-center">
                        <div>
                            <h1>Admin Dashboard</h1>
                            <p className="text-muted">Logged in as: {adminEmail}</p>
                        </div>
                        <div>
                            <button
                                className="btn btn-outline-primary me-2"
                                onClick={() => setShowConfig(!showConfig)}
                            >
                                ⚙️ Configuration
                            </button>
                            <button className="btn btn-outline-secondary" onClick={handleLogout}>
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Configuration Panel */}
            {showConfig && (
                <div className="row mb-4">
                    <div className="col-md-6">
                        <div className="card">
                            <div className="card-body">
                                <h5 className="card-title">System Configuration</h5>
                                {configMessage && (
                                    <div
                                        className={`alert ${configMessage.includes("Error")
                                                ? "alert-danger"
                                                : "alert-success"
                                            }`}
                                    >
                                        {configMessage}
                                    </div>
                                )}
                                <form onSubmit={handleConfigSubmit}>
                                    <div className="mb-3">
                                        <label className="form-label">
                                            Max Questions per Interview
                                        </label>
                                        <input
                                            type="number"
                                            className="form-control"
                                            min="1"
                                            max="50"
                                            value={config.MAX_QUESTIONS}
                                            onChange={(e) =>
                                                setConfig({ ...config, MAX_QUESTIONS: e.target.value })
                                            }
                                            disabled={configLoading}
                                        />
                                        <small className="text-muted">Range: 1-50</small>
                                    </div>

                                    <div className="mb-3">
                                        <label className="form-label">
                                            Question Timeout (seconds)
                                        </label>
                                        <input
                                            type="number"
                                            className="form-control"
                                            min="30"
                                            max="600"
                                            value={config.QUESTION_TIMEOUT_SECONDS}
                                            onChange={(e) =>
                                                setConfig({
                                                    ...config,
                                                    QUESTION_TIMEOUT_SECONDS: e.target.value,
                                                })
                                            }
                                            disabled={configLoading}
                                        />
                                        <small className="text-muted">Range: 30-600 seconds</small>
                                    </div>

                                    <button
                                        type="submit"
                                        className="btn btn-primary"
                                        disabled={configLoading}
                                    >
                                        {configLoading ? "Saving..." : "Save Configuration"}
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Filters */}
            <div className="row mb-3">
                <div className="col">
                    <div className="card">
                        <div className="card-body">
                            <h6 className="card-title">Filters</h6>
                            <div className="row g-2">
                                <div className="col-md-4">
                                    <input
                                        type="text"
                                        className="form-control"
                                        placeholder="Filter by email..."
                                        value={filters.email}
                                        onChange={(e) => handleFilterChange("email", e.target.value)}
                                    />
                                </div>
                                <div className="col-md-3">
                                    <select
                                        className="form-select"
                                        value={filters.role}
                                        onChange={(e) => handleFilterChange("role", e.target.value)}
                                    >
                                        <option value="">All Roles</option>
                                        <option value="Software Developer">Software Developer</option>
                                        <option value="Project Leader">Project Leader</option>
                                        <option value="Data Analyst">Data Analyst</option>
                                        <option value="UX Designer">UX Designer</option>
                                        <option value="QA Engineer">QA Engineer</option>
                                        <option value="Product Manager">Product Manager</option>
                                    </select>
                                </div>
                                <div className="col-md-auto">
                                    <button className="btn btn-primary" onClick={applyFilters}>
                                        Apply Filters
                                    </button>
                                </div>
                                <div className="col-md-auto">
                                    <button className="btn btn-secondary" onClick={clearFilters}>
                                        Clear
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Interviews Table */}
            <div className="row">
                <div className="col">
                    <div className="card">
                        <div className="card-body">
                            <h5 className="card-title mb-3">
                                Interviews
                                <span className="badge bg-primary ms-2">{interviews.length}</span>
                            </h5>

                            {loading ? (
                                <div className="text-center py-5">
                                    <div className="spinner-border" role="status">
                                        <span className="visually-hidden">Loading...</span>
                                    </div>
                                </div>
                            ) : interviews.length === 0 ? (
                                <div className="alert alert-info">No interviews found</div>
                            ) : (
                                <>
                                    <div className="table-responsive">
                                        <table className="table table-hover">
                                            <thead>
                                                <tr>
                                                    <th>Candidate</th>
                                                    <th>Email</th>
                                                    <th>Role</th>
                                                    <th>Date</th>
                                                    <th>Score</th>
                                                    <th>Status</th>
                                                    <th>Actions</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {interviews.map((interview) => (
                                                    <tr key={interview.id}>
                                                        <td>
                                                            {interview.candidates?.first_name || ""}{" "}
                                                            {interview.candidates?.last_name || "N/A"}
                                                        </td>
                                                        <td>{interview.candidates?.email || "N/A"}</td>
                                                        <td>
                                                            <span className="badge bg-info">
                                                                {interview.role_applied}
                                                            </span>
                                                        </td>
                                                        <td className="small">
                                                            {formatDate(interview.start_time)}
                                                        </td>
                                                        <td>
                                                            {interview.final_score ? (
                                                                <strong>{interview.final_score.toFixed(2)}</strong>
                                                            ) : (
                                                                <span className="text-muted">-</span>
                                                            )}
                                                        </td>
                                                        <td>
                                                            {interview.end_time ? (
                                                                <span className="badge bg-success">Completed</span>
                                                            ) : (
                                                                <span className="badge bg-warning">In Progress</span>
                                                            )}
                                                        </td>
                                                        <td>
                                                            <button
                                                                className="btn btn-sm btn-outline-primary"
                                                                onClick={() => viewInterview(interview.id)}
                                                            >
                                                                View Details
                                                            </button>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>

                                    {/* Pagination */}
                                    {totalPages > 1 && (
                                        <div className="d-flex justify-content-center mt-3">
                                            <nav>
                                                <ul className="pagination">
                                                    <li className={`page-item ${page === 1 ? "disabled" : ""}`}>
                                                        <button
                                                            className="page-link"
                                                            onClick={() => loadInterviews(page - 1)}
                                                            disabled={page === 1}
                                                        >
                                                            Previous
                                                        </button>
                                                    </li>
                                                    {[...Array(totalPages)].map((_, idx) => (
                                                        <li
                                                            key={idx}
                                                            className={`page-item ${page === idx + 1 ? "active" : ""
                                                                }`}
                                                        >
                                                            <button
                                                                className="page-link"
                                                                onClick={() => loadInterviews(idx + 1)}
                                                            >
                                                                {idx + 1}
                                                            </button>
                                                        </li>
                                                    ))}
                                                    <li
                                                        className={`page-item ${page === totalPages ? "disabled" : ""
                                                            }`}
                                                    >
                                                        <button
                                                            className="page-link"
                                                            onClick={() => loadInterviews(page + 1)}
                                                            disabled={page === totalPages}
                                                        >
                                                            Next
                                                        </button>
                                                    </li>
                                                </ul>
                                            </nav>
                                        </div>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
