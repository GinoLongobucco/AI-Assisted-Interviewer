"use client";
import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { getInterviewResults } from "@/services/InterviewService";


export default function ResultsPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const interviewId = searchParams.get("id");

    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!interviewId) {
            setError("No interview ID provided");
            setLoading(false);
            return;
        }

        const fetchResults = async () => {
            try {
                const data = await getInterviewResults(interviewId);
                setResults(data);
                setLoading(false);
            } catch (err) {
                console.error("Error fetching results:", err);
                setError(err.message);
                setLoading(false);
            }
        };

        fetchResults();
    }, [interviewId]);


    if (loading) {
        return (
            <div className="container py-5 text-center">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Cargando...</span>
                </div>
                <p className="mt-3">Cargando resultados...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container py-5">
                <div className="alert alert-danger">
                    <h4>Error</h4>
                    <p>{error}</p>
                    <button className="btn btn-primary" onClick={() => router.push("/")}>
                        Volver al inicio
                    </button>
                </div>
            </div>
        );
    }

    if (!results) {
        return null;
    }

    const getScoreColor = (score) => {
        if (score >= 4) return "success";
        if (score >= 3) return "warning";
        return "danger";
    };

    const getScoreLabel = (score) => {
        if (score === 5) return "Excelente";
        if (score === 4) return "Bueno";
        if (score === 3) return "Aceptable";
        if (score === 2) return "Parcial";
        return "Incorrecto";
    };

    return (
        <div className="container py-5">
            <div className="row justify-content-center">
                <div className="col-md-10 col-lg-8">

                    {/* Header */}
                    <div className="text-center mb-5">
                        <h1>Resultados de la Entrevista</h1>
                        <h4 className="text-muted">Rol: {results.role}</h4>
                    </div>

                    {/* Summary Card */}
                    <div className="card shadow-lg mb-4">
                        <div className="card-body text-center p-5">
                            <h2 className="mb-4">Resumen de Puntuación</h2>

                            <div className="row">
                                <div className="col-md-4 mb-3">
                                    <h6 className="text-muted">Puntuación Total</h6>
                                    <h1 className="text-primary">{results.total_score}</h1>
                                    <p className="text-muted">de {results.max_possible_score} puntos</p>
                                </div>

                                <div className="col-md-4 mb-3">
                                    <h6 className="text-muted">Promedio</h6>
                                    <h1 className="text-primary">{results.average_score}</h1>
                                    <p className="text-muted">de 5.0</p>
                                </div>

                                <div className="col-md-4 mb-3">
                                    <h6 className="text-muted">Preguntas Respondidas</h6>
                                    <h1 className="text-primary">{results.questions_answered}</h1>
                                    <p className="text-muted">de {results.total_questions}</p>
                                </div>
                            </div>

                            {/* Overall assessment */}
                            <div className="mt-4">
                                {results.average_score >= 4 && (
                                    <div className="alert alert-success">
                                        <strong>¡Excelente trabajo!</strong> Has demostrado un sólido conocimiento y habilidades.
                                    </div>
                                )}
                                {results.average_score >= 3 && results.average_score < 4 && (
                                    <div className="alert alert-warning">
                                        <strong>Buen desempeño.</strong> Hay áreas donde puedes mejorar.
                                    </div>
                                )}
                                {results.average_score < 3 && (
                                    <div className="alert alert-info">
                                        <strong>Sigue practicando.</strong> Considera reforzar tus conocimientos en las áreas evaluadas.
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Detailed Results */}
                    <h3 className="mb-4">Detalles por Pregunta</h3>

                    {results.answers.map((answer, index) => (
                        <div key={index} className="card shadow-sm mb-4">
                            <div className="card-body">
                                <div className="d-flex justify-content-between align-items-start mb-3">
                                    <h5 className="mb-0">Pregunta {index + 1}</h5>
                                    <span className={`badge bg-${getScoreColor(answer.score)} fs-6`}>
                                        {answer.score}/5 - {getScoreLabel(answer.score)}
                                    </span>
                                </div>

                                <div className="mb-3">
                                    <strong>Pregunta:</strong>
                                    <p className="text-primary">{answer.question}</p>
                                </div>

                                <div className="mb-3">
                                    <strong>Tu respuesta:</strong>
                                    <p className="text-muted fst-italic">{answer.transcription}</p>
                                </div>

                                <div className="mb-0">
                                    <strong>Evaluación:</strong>
                                    <p className="text-muted">{answer.reasoning}</p>
                                </div>
                            </div>
                        </div>
                    ))}

                    {/* Actions */}
                    <div className="text-center mt-5">
                        <button
                            className="btn btn-primary btn-lg px-5"
                            onClick={() => {
                                localStorage.clear();
                                router.push("/");
                            }}
                        >
                            Nueva Entrevista
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
