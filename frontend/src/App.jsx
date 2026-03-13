import React, { useEffect, useState } from 'react';
import SystemMetrics from './components/SystemMetrics';
import AnomalyChart from './components/AnomalyChart';
import AlertPanel from './components/AlertPanel';
import EventTable from './components/EventTable';
import { useWebSocket } from './hooks/useWebSocket';
import { fetchMetrics, fetchAnomalies } from './lib/api';

function App() {
  const { isConnected, messages: wsEvents } = useWebSocket();
  const [metrics, setMetrics] = useState(null);
  const [historicalAnomalies, setHistoricalAnomalies] = useState([]);

  // Fetch initial REST data
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [metricsData, anomaliesData] = await Promise.all([
          fetchMetrics(),
          fetchAnomalies(50)
        ]);
        setMetrics(metricsData);
        setHistoricalAnomalies(anomaliesData);
      } catch (err) {
        console.error("Failed to load initial REST data:", err);
      }
    };
    
    loadInitialData();
    // Refresh metrics periodically (every 5 seconds)
    const interval = setInterval(loadInitialData, 5000);
    return () => clearInterval(interval);
  }, []);

  // Compute live active anomalies from WebSocket combined with historical
  const liveAnomalies = wsEvents.filter(e => e.is_anomaly);
  // Merge historical and live anomalies (deduplicated by ID loosely, or just concat and slice)
  // Here we just keep the 20 most recent unique anomalies
  const combinedAnomalies = [...liveAnomalies, ...historicalAnomalies]
    .filter((v, i, a) => a.findIndex(t => (t.id === v.id)) === i)
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    .slice(0, 10);

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <span className="font-bold text-xl text-indigo-600">AnomalyX</span>
              </div>
            </div>
            <div className="flex items-center">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {isConnected ? 'Stream Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-4 sm:px-0 flex flex-col space-y-6">
          
          {/* Top level metrics */}
          <section>
            <SystemMetrics metrics={metrics} />
          </section>

          {/* Charts & Alerts Grid */}
          <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <AnomalyChart data={wsEvents} />
            </div>
            <div className="lg:col-span-1">
              <AlertPanel anomalies={combinedAnomalies} />
            </div>
          </section>

          {/* Table */}
          <section>
            <EventTable events={wsEvents} />
          </section>

        </div>
      </div>
    </div>
  );
}

export default App;
