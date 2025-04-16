import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const TopSkillsChart = ({ skills = [] }) => {
    if (!skills || skills.length === 0) {
        return (
            <div className="bg-white p-4 rounded-lg shadow-md text-center">
                <h3 className="text-xl font-semibold mb-2">🔥 Top Skills from Resumes</h3>
                <p className="text-gray-500 italic">No skills data available.</p>
            </div>
        );
    }

    const data = skills.map(([skill, count]) => ({ skill, count }));

    return (
        <div className="bg-white p-4 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-2">🔥 Top Skills from Resumes</h3>
            <ResponsiveContainer width="100%" height={250}>
                <BarChart data={data}>
                    <XAxis dataKey="skill" angle={-45} textAnchor="end" interval={0} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#3182CE" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

export default TopSkillsChart;
