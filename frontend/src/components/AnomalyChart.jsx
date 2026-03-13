import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';

export default function AnomalyChart({ data, threshold = 0.85 }) {
  // Extract proper timestamp and limit max items for clarity if needed
  const chartData = (data || []).map((d) => {
    const date = new Date(d.timestamp);
    return {
      time: `${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`,
      score: d.anomaly_score,
      isAnomaly: d.is_anomaly
    };
  }).reverse(); // Reverse if the incoming data is newest-first

  return (
    <div className="bg-white shadow rounded-lg p-4">
      <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
        Real-Time Anomaly Scores
      </h3>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis domain={[-2, 6]} /> {/* Z-scores usually between -3 and 3, but anomalies might be higher */}
            <Tooltip />
            
            {/* Draw a line for anomaly score threshold if you want to visualize it.
                Wait, isolation forest or robust scaled scores might not have a fixed upper limit.
                Using 2.0 as a static example threshold here just for visualization. */}
            <ReferenceLine y={2.0} label="Threshold" stroke="red" strokeDasharray="3 3" />
            
            <Line 
              type="monotone" 
              dataKey="score" 
              stroke="#4F46E5" 
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 8 }} 
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
