import React from "react";

const MatchScoreStats = ({ totalResumes, avgScore, rating }) => {
    return (
        <div className="bg-gray-100 p-4 rounded-lg shadow-md mb-4">
            <p className="text-xl font-semibold">📄 Total Resumes: {totalResumes ?? "N/A"}</p>
            <p className="text-lg text-blue-600">
                ⚡ Average Match Score: {avgScore !== undefined && avgScore !== null ? avgScore.toFixed(2) : "N/A"}
            </p>
            <p className="text-lg text-green-600">
                ⭐ Recruiter Rating: {rating !== undefined && rating !== null ? rating.toFixed(2) : "N/A"} / 5
            </p>
        </div>
    );
};

export default MatchScoreStats;
