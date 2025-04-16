import React, { useState, useEffect } from "react";
import axios from "axios";
import TopSkillsChart from "./TopSkillsChart";
import FeedbackList from "./FeedbackList";
import MatchScoreStats from "./MatchScoreStats";

const AdminDashboard = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    axios
      .get("http://127.0.0.1:8000/admin_dashboard/")
      .then((response) => {
        setData(response.data);
        setIsLoading(false);
      })
      .catch((error) => {
        setError("Failed to load dashboard data.");
        console.error("Error fetching data:", error);
        setIsLoading(false);
      });
  }, []);

  if (isLoading) return <p>Loading...</p>;

  if (error) return <p className="text-red-500">{error}</p>;

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Admin Dashboard</h2>
      {data && (
        <>
          <MatchScoreStats
            totalResumes={data.total_resumes}
            avgScore={data.average_match_score}
            rating={data.recruiter_average_rating}
          />
          <TopSkillsChart skills={data.top_skills} />
          <FeedbackList feedbackCount={data.feedback_count} />
        </>
      )}
    </div>
  );
};

export default AdminDashboard;
