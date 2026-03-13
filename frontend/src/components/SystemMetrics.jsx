import React from 'react';
import { Activity, ShieldAlert, Users, Database } from 'lucide-react';

export default function SystemMetrics({ metrics }) {
  if (!metrics) {
    return (
      <div className="bg-white shadow rounded-lg p-4 grid grid-cols-2 gap-4 lg:grid-cols-4 animate-pulse">
        {[1, 2, 3, 4].map(idx => (
          <div key={idx} className="h-24 bg-gray-100 rounded-lg"></div>
        ))}
      </div>
    );
  }

  const { total_observed, anomaly_count, anomaly_rate } = metrics;
  
  const stats = [
    { 
      name: 'Total Events', 
      value: total_observed || 0, 
      icon: Activity,
      color: 'text-blue-500',
      bgColor: 'bg-blue-100'
    },
    { 
      name: 'Anomalies Detected', 
      value: anomaly_count || 0, 
      icon: ShieldAlert,
      color: 'text-red-500',
      bgColor: 'bg-red-100'
    },
    { 
      name: 'Anomaly Rate', 
      value: anomaly_rate != null ? `${(anomaly_rate * 100).toFixed(2)}%` : '0%', 
      icon: Database,
      color: 'text-amber-500',
      bgColor: 'bg-amber-100'
    },
    { 
      name: 'Active Users', 
      value: 'Live', // Placeholder since real active user tracking isn't explicitly in the current backend
      icon: Users,
      color: 'text-green-500',
      bgColor: 'bg-green-100'
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      {stats.map((item) => (
        <div key={item.name} className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className={`p-3 rounded-md ${item.bgColor}`}>
                  <item.icon className={`h-6 w-6 ${item.color}`} aria-hidden="true" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">{item.name}</dt>
                  <dd>
                    <div className="text-lg font-medium text-gray-900">{item.value}</div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
