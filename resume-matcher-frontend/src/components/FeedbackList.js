import React from "react";

const FeedbackList = ({ feedbackCount = 0 }) => {
    return (
        <div className="bg-gray-100 p-4 rounded-lg shadow-md mt-4">
            <h3 className="text-lg font-semibold">📝 Feedback from Recruiters</h3>
            {feedbackCount > 0 ? (
                <p className="text-gray-700">Total Feedback Received: {feedbackCount}</p>
            ) : (
                <p className="text-gray-500 italic">No feedback received yet.</p>
            )}
        </div>
    );
};

export default FeedbackList;
