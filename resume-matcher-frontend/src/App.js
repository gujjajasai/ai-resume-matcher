import React, { useState } from "react";
import AdminDashboard from "./components/AdminDashboard";

function ResumeMatcher() {
    const [resume, setResume] = useState(null);
    const [jobDescription, setJobDescription] = useState("");
    const [result, setResult] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleFileChange = (event) => {
        setResume(event.target.files[0]);
    };

    const handleSubmit = async () => {
        if (!resume || !jobDescription) {
            setError("⚠️ Please upload a resume and enter a job description.");
            return;
        }

        setLoading(true);
        setError("");
        setResult("");

        const formData = new FormData();
        formData.append("file", resume);
        formData.append("job_description", jobDescription);

        try {
            const response = await fetch("http://127.0.0.1:8000/match-resume/", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Error: ${response.status}`);
            }

            const data = await response.json();
            setResult(`✅ Match Score: ${data.match_score}%`);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col items-center p-6 bg-gray-100 min-h-screen">
            <h2 className="text-3xl font-bold mb-6">🚀 AI Resume Matcher</h2>

            {/* File Upload */}
            <input
                type="file"
                onChange={handleFileChange}
                accept=".pdf,.docx"
                className="mb-2 border p-2 rounded w-full max-w-md"
            />
            {resume && <p className="text-sm text-gray-500">📁 {resume.name}</p>}

            {/* Job Description Input */}
            <textarea
                rows="4"
                cols="50"
                placeholder="✍️ Enter Job Description"
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                className="border p-2 w-full max-w-md rounded mt-3"
            />

            {/* Submit Button */}
            <button
                onClick={handleSubmit}
                disabled={loading}
                className="bg-blue-600 text-white px-6 py-2 mt-4 rounded hover:bg-blue-700 flex items-center"
            >
                {loading ? (
                    <>
                        <svg
                            className="animate-spin h-5 w-5 mr-2"
                            viewBox="0 0 24 24"
                        >
                            <circle
                                className="opacity-25"
                                cx="12"
                                cy="12"
                                r="10"
                                stroke="white"
                                strokeWidth="4"
                                fill="none"
                            />
                            <path
                                className="opacity-75"
                                fill="white"
                                d="M4 12a8 8 0 018-8v8H4z"
                            />
                        </svg>
                        Processing...
                    </>
                ) : (
                    "Match Resume"
                )}
            </button>

            {/* Error Message */}
            {error && (
                <div className="mt-4 bg-red-100 text-red-700 px-4 py-2 rounded w-full max-w-md text-center">
                    {error}
                </div>
            )}

            {/* Success Message */}
            {result && (
                <div className="mt-4 bg-green-100 text-green-700 px-4 py-2 rounded w-full max-w-md text-center">
                    {result}
                </div>
            )}
        </div>
    );
}

function App() {
    const [showAdmin, setShowAdmin] = useState(false);

    return (
        <div>
            <nav className="p-4 bg-gray-800 text-white flex justify-between">
                <div>
                    <button onClick={() => setShowAdmin(false)} className="mr-4 px-4 py-2 bg-blue-500 rounded hover:bg-blue-600">
                        🏠 Home
                    </button>
                    <button onClick={() => setShowAdmin(true)} className="px-4 py-2 bg-green-500 rounded hover:bg-green-600">
                        🛠 Admin Dashboard
                    </button>
                </div>
            </nav>

            {showAdmin ? <AdminDashboard /> : <ResumeMatcher />}
        </div>
    );
}

export default App;
