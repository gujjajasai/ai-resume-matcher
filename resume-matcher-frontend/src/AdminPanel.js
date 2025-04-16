import React, { useEffect, useState } from "react";

function AdminPanel() {
    const [data, setData] = useState(null);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem("access_token");
        if (!token) {
            setError("❌ Unauthorized: Please log in first.");
            setLoading(false);
            return;
        }

        fetch("http://127.0.0.1:8000/admin_dashboard/", {
            method: "GET",
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        })
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            setData(data);
            setLoading(false);
        })
        .catch((error) => {
            setError("⚠️ Failed to load dashboard data.");
            console.error("Error fetching admin data:", error);
            setLoading(false);
        });
    }, []);

    if (loading) return <p className="text-gray-600 text-center mt-4">⏳ Loading dashboard...</p>;

    if (error) 
        return (
            <div className="text-center text-red-600 bg-red-100 p-4 rounded-lg mt-4">
                {error}
            </div>
        );

    return (
        <div className="p-6 bg-gray-100 min-h-screen">
            <h1 className="text-3xl font-bold text-center mb-6">📊 Admin Dashboard</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Total Resumes Processed */}
                <div className="bg-blue-100 p-4 rounded-lg shadow-md">
                    <h3 className="text-xl font-semibold">📄 Total Resumes</h3>
                    <p className="text-2xl font-bold">{data.total_resumes}</p>
                </div>

                {/* Average Match Score */}
                <div className="bg-green-100 p-4 rounded-lg shadow-md">
                    <h3 className="text-xl font-semibold">📈 Avg. Match Score</h3>
                    <p className="text-2xl font-bold">
                        {data.average_match_score ? `${data.average_match_score.toFixed(2)}%` : "N/A"}
                    </p>
                </div>

                {/* Top Skills */}
                <div className="bg-yellow-100 p-4 rounded-lg shadow-md">
                    <h3 className="text-xl font-semibold">🏆 Top Skills</h3>
                    <ul className="mt-2 text-gray-700">
                        {Array.isArray(data.top_skills) && data.top_skills.length > 0 ? (
                            data.top_skills.map(([skill, count]) => (
                                <li key={skill} className="text-sm">
                                    <strong>{skill}</strong> ({count} times)
                                </li>
                            ))
                        ) : (
                            <p className="text-sm">No top skills available.</p>
                        )}
                    </ul>
                </div>
            </div>

            {/* Processed Resumes */}
            <h3 className="text-2xl font-bold mt-8">📂 Processed Resumes</h3>
            <ul className="bg-white p-4 rounded-lg shadow-md mt-4">
                {Array.isArray(data.processed_resumes) && data.processed_resumes.length > 0 ? (
                    data.processed_resumes.map((resume, index) => (
                        <li 
                            key={index} 
                            className="p-2 border-b last:border-none hover:bg-gray-200 transition rounded-lg"
                        >
                            <strong>{resume.filename}</strong> - Match Score:{" "}
                            {resume.match_score ? `${resume.match_score.toFixed(2)}%` : "N/A"}
                        </li>
                    ))
                ) : (
                    <p className="text-gray-500">No resumes processed yet.</p>
                )}
            </ul>
        </div>
    );
}

export default AdminPanel;
