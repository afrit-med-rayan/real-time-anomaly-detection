import React from 'react';
import { AlertTriangle, Clock } from 'lucide-react';

export default function AlertPanel({ anomalies }) {
  if (!anomalies || anomalies.length === 0) {
    return (
      <div className="bg-white shadow rounded-lg p-4">
        <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4 flex items-center">
          <AlertTriangle className="h-5 w-5 text-gray-400 mr-2" />
          Recent Alerts
        </h3>
        <p className="text-sm text-gray-500 text-center py-4">No recent anomalies detected.</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg p-4">
      <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4 flex items-center">
        <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
        Recent Alerts
      </h3>
      <div className="flow-root">
        <ul className="-mb-8">
          {anomalies.map((anomaly, eventIdx) => {
            const date = new Date(anomaly.timestamp);
            return (
              <li key={anomaly.id || eventIdx}>
                <div className="relative pb-8">
                  {eventIdx !== anomalies.length - 1 ? (
                    <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true" />
                  ) : null}
                  <div className="relative flex space-x-3">
                    <div>
                      <span className="h-8 w-8 rounded-full bg-red-100 flex items-center justify-center ring-8 ring-white">
                        <AlertTriangle className="h-4 w-4 text-red-600" aria-hidden="true" />
                      </span>
                    </div>
                    <div className="flex-1 pt-1.5 flex justify-between space-x-4">
                      <div>
                        <p className="text-sm text-gray-500">
                          High anomaly score <span className="font-semibold text-gray-900">{anomaly.anomaly_score?.toFixed(3)}</span> for User <span className="font-medium text-gray-900">{anomaly.user_id}</span>
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                          Action: {anomaly.action} | Item: {anomaly.item_id}
                        </p>
                      </div>
                      <div className="text-right text-xs whitespace-nowrap text-gray-500 flex flex-col items-end">
                        <span className="flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          {date.toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
