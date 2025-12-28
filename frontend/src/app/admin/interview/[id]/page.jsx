"use client";
import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { getInterviewDetail, isAuthenticated } from "@/services/AdminService";

export default function InterviewDetailPage() {
    const router = useRouter();
    const params = useParams();
    const interviewId = params.id;

    const [interview, setInterview] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        if (!isAuthenticated()) {
            router.push("/admin/login");
            return;
        }

        if (interviewId) {
            loadInterview();
        }
    }, [interviewId]);

    const loadInterview = async () => {
        try {
            setLoading(true);
            const data = await getInterviewDetail(interviewId);
            setInterview(data);
        } catch (err) {
            setError(err.message || "Error loading interview");
            if (err.message.includes("Authentication")) {
                router.push("/admin/login");
            }
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return "N/A";
        const date = new Date(dateString);
        return date.toLocaleString();
    };

    const getScoreBadgeClass = (score) => {
        if (score >= 4.5) return "bg-success";
        if (score >= 3.5) return "bg-primary";
        if (score >= 2.5) return "bg-warning";
        return "bg-danger";
    };

    if (loading) {
        return (
            <div className="container py-5">
                <div className="text-center">
                    <div className="spinner-border" role="status">
                        <span className="visually-hidden">Loading...</span>
                    </div>
                    <p className="mt-2">Loading interview details...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container py-5">
                <div className="alert alert-danger">
                    <h4>Error</h4>
                    <p>{error}</p>
                    <button
                        className="btn btn-primary mt-2"
                        onClick={() => router.push("/admin/dashboard")}
                    >
                        Back to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    if (!interview) {
        return (
            <div className="container py-5">
                <div className="alert alert-warning">Interview not found</div>
            </div>
        );
    }

    return (
        <div className="container py-4">
            {/* Header */}
            <div className="row mb-4">
                <div className="col">
                    <button
                        className="btn btn-outline-secondary mb-3"
                        onClick={() => router.push("/admin/dashboard")}
                    >
                        ← Back to Dashboard
                    </button>
                    <h1>Interview Details</h1>
                </div>
            </div>

            {/* Candidate Info */}
            <div className="row mb-4">
                <div className="col-md-6">
                    <div className="card">
                        <div className="card-body">
                            <h5 className="card-title">Candidate Information</h5>
                            <table className="table table-sm">
                                <tbody>
                                    <tr>
                                        <th>Name:</th>
                                        <td>
                                            {interview.candidate?.first_name || ""}{" "}
                                            {interview.candidate?.last_name || "N/A"}
                                        </td>
                                    </tr>
                                    <tr>
                                        <th>Email:</th>
                                        <td>{interview.candidate?.email || "N/A"}</td>
                                    </tr>
                                    <tr>
                                        <th>Role Applied:</th>
                                        <td>
                                            <span className="badge bg-info">{interview.role}</span>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div className="col-md-6">
                    <div className="card">
                        <div className="card-body">
                            <h5 className="card-title">Interview Statistics</h5>
                            <table className="table table-sm">
                                <tbody>
                                    <tr>
                                        <th>Start Time:</th>
                                        <td>{formatDate(interview.start_time)}</td>
                                    </tr>
                                    <tr>
                                        <th>End Time:</th>
                                        <td>
                                            {interview.end_time ? formatDate(interview.end_time) : (
                                                <span className="badge bg-warning">In Progress</span>
                                            )}
                                        </td>
                                    </tr>
                                    <tr>
                                        <th>Status:</th>
                                        <td>
                                            {interview.status === "completed" ? (
                                                <span className="badge bg-success">Completed</span>
                                            ) : (
                                                <span className="badge bg-warning">In Progress</span>
                                            )}
                                        </td>
                                    </tr>
                                    <tr>
                                        <th>Questions Answered:</th>
                                        <td>
                                            {interview.statistics?.answers_submitted || 0} /{" "}
                                            {interview.statistics?.total_questions || 0}
                                        </td>
                                    </tr>
                                    <tr>
                                        <th>Total Score:</th>
                                        <td>
                                            <strong>{interview.statistics?.total_score || 0}</strong> /{" "}
                                            {interview.statistics?.max_possible_score || 0}
                                        </td>
                                    </tr>
                                    <tr>
                                        <th>Average Score:</th>
                                        <td>
                                            <span
                                                className={`badge ${getScoreBadgeClass(
                                                    interview.statistics?.average_score || 0
                                                )}`}
                                            >
                                                {interview.statistics?.average_score?.toFixed(2) || "0.00"} / 5.00
                                            </span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <th>Completion:</th>
                                        <td>
                                            {interview.statistics?.completion_percentage || 0}%
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            {/* Questions and Answers */}
            <div className="row">
                <div className="col">
                    <div className="card">
                        <div className="card-body">
                            <h5 className="card-title mb-4">Questions and Answers</h5>

                            {interview.answers && interview.answers.length > 0 ? (
                                interview.answers.map((answer, idx) => (
                                    <div key={answer.id} className="mb-4 pb-4 border-bottom">
                                        <div className="d-flex justify-content-between align-items-start mb-2">
                                            <h6 className="mb-0">
                                                Question {idx + 1}
                                                <span
                                                    className={`badge ${getScoreBadgeClass(
                                                        answer.score || 0
                                                    )} ms-2`}
                                                >
                                                    Score: {answer.score?.toFixed(1) || "0.0"} / 5.0
                                                </span>
                                            </h6>
                                            <small className="text-muted">
                                                {formatDate(answer.created_at)}
                                            </small>
                                        </div>

                                        <div className="alert alert-light mb-2">
                                            <strong>Q:</strong> {answer.questions?.content || "N/A"}
                                        </div>

                                        <div className="mb-2">
                                            <strong>Answer (Transcription):</strong>
                                            <p className="mb-0 mt-1 p-3 bg-light rounded">
                                                {answer.transcript || "No answer provided"}
                                            </p>
                                        </div>

                                        {answer.feedback && (
                                            <div className="alert alert-info mb-0">
                                                <strong>AI Evaluation:</strong>
                                                <p className="mb-0 mt-1">{answer.feedback}</p>
                                            </div>
                                        )}
                                    </div>
                                ))
                            ) : (
                                <div className="alert alert-warning">
                                    No answers have been submitted yet.
                                </div>
                            )}

                            {/* Unanswered Questions */}
                            {interview.questions &&
                                interview.answers &&
                                interview.questions.length > interview.answers.length && (
                                    <div className="mt-4">
                                        <h6 className="text-muted">Remaining Questions:</h6>
                                        {interview.questions
                                            .slice(interview.answers.length)
                                            .map((question, idx) => (
                                                <div key={question.id} className="alert alert-secondary">
                                                    <strong>
                                                        Question {interview.answers.length + idx + 1}:
                                                    </strong>{" "}
                                                    {question.content}
                                                </div>
                                            ))}
                                    </div>
                                )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Actions */}
            <div className="row mt-4">
                <div className="col text-center">
                    <button
                        className="btn btn-primary"
                        onClick={() => router.push("/admin/dashboard")}
                    >
                        Back to Dashboard
                    </button>
                </div>
            </div>
        </div>
    );
}
