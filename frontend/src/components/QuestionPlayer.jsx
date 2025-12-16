"use client";
import { useState, useRef, useEffect } from "react";

export default function QuestionPlayer({ interviewId, questionNum }) {
    const [isPlaying, setIsPlaying] = useState(false);
    const audioRef = useRef(null);

    // Stop audio when question changes
    useEffect(() => {
        // Stop any playing audio when question number changes
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current = null;
            setIsPlaying(false);
        }
    }, [questionNum]); // Trigger when question number changes

    const playQuestion = async () => {
        try {
            // Stop any currently playing audio
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current = null;
            }

            setIsPlaying(true);

            // Add questionNum to URL to prevent browser caching
            const url = `http://localhost:8000/ai/question-audio/${interviewId}?q=${questionNum}&t=${Date.now()}`;

            // Create audio element
            const audio = new Audio(url);
            audioRef.current = audio;

            audio.onended = () => {
                setIsPlaying(false);
                audioRef.current = null;
            };

            audio.onerror = () => {
                setIsPlaying(false);
                audioRef.current = null;
                console.error("Error playing audio");
            };

            await audio.play();

        } catch (error) {
            console.error("Error playing question:", error);
            setIsPlaying(false);
            audioRef.current = null;
        }
    };

    const stopAudio = () => {
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current = null;
            setIsPlaying(false);
        }
    };

    return (
        <div className="d-flex gap-2">
            <button
                className="btn btn-outline-primary btn-sm"
                onClick={playQuestion}
                disabled={isPlaying}
            >
                {isPlaying ? (
                    <>
                        <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                        Reproduciendo...
                    </>
                ) : (
                    <>
                        Escuchar
                    </>
                )}
            </button>
            {isPlaying && (
                <button
                    className="btn btn-outline-danger btn-sm"
                    onClick={stopAudio}
                >
                    Detener
                </button>
            )}
        </div>
    );
}
