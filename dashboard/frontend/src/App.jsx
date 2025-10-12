import React from 'react';
import { useState, useEffect } from 'react';
import ClientTable from './components/ClientTable.jsx';

function App() {
  const [clients, setClients] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);  // Added loading state

  const fetchClients = async (retries = 3) => {
    try {
      // Docker: Use service name; fallback to localhost for local dev
      const apiUrl = process.env.NODE_ENV === 'development' 
        ? 'http://localhost:8000/api/clients' 
        : 'http://backend:8000/api/clients';
      
      console.log('Fetching from:', apiUrl);  // Debug log
      
      const res = await fetch(apiUrl);
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      const data = await res.json();
      setClients(data);
      console.log('Fetched clients:', data);  // Debug log
    } catch (err) {
      console.error('Error fetching clients:', err);
      if (retries > 0) {
        console.log(`Retrying in 1s... (${retries} left)`);
        setTimeout(() => fetchClients(retries - 1), 1000);
      } else {
        setError('Failed to load clients. Check backend & Docker network.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClients();
  }, []);

  if (error) {
    return <div className="p-8 text-red-400">Error: {error}</div>;
  }

  if (loading) {
    return <div className="p-8 text-gray-400">Loading clients...</div>;
  }

  // Compute dynamic stats
  const totalClients = clients.length;
  const impactedClients = clients.filter(c => c.newRegulation !== "N/A" && c.deadline !== null).length;
  const percentageImpacted = totalClients > 0 ? (impactedClients / totalClients) : 0;
  const dashOffsetImpacted = 283 * (1 - percentageImpacted);

  const uniqueNewRegs = [...new Set(clients.filter(c => c.newRegulation !== "N/A" && c.newRegulation !== "UNDER REVIEW" && c.newRegulation !== "MONITORED").map(c => c.newRegulation))].length;
  const percentageNewRegs = totalClients > 0 ? (uniqueNewRegs / totalClients) : 0;
  const dashOffsetNewRegs = 283 * (1 - percentageNewRegs);

  // Urgency calculation
  const currentDate = new Date('2025-10-12');
  let urgencyLevel = 'LOW';
  let urgencyColor = 'text-green-400';
  for (const c of clients) {
    if (c.deadline) {
      const deadline = new Date(c.deadline);
      const daysUntilDeadline = (deadline - currentDate) / (1000 * 60 * 60 * 24);
      if (daysUntilDeadline <= 90) {
        urgencyLevel = 'HIGH';
        urgencyColor = 'text-red-500';
        break;
      } else if (daysUntilDeadline <= 180) {
        urgencyLevel = 'MEDIUM';
        urgencyColor = 'text-yellow-500';
      }
    }
  }
  // Dynamic offset for urgency circle (HIGH: ~80% empty/20% filled, MED: 50%, LOW: 100% empty)
  const dashOffsetUrgency = urgencyLevel === 'HIGH' ? 283 * 0.8 : urgencyLevel === 'MEDIUM' ? 283 * 0.5 : 283;

  return (
    <div className="p-4 sm:p-6 md:p-8">
      <div className="main-container max-w-7xl mx-auto bg-[#0a192f] border border-[#1e2d4a] rounded-xl p-8">
        {/* Header */}
        <header className="flex justify-between items-center mb-8">
          <div className="flex items-center space-x-4">
            <div className="bg-gray-700 p-3 rounded-lg">
              <span className="font-bold text-xl">AS</span>
            </div>
          </div>
          <div className="text-center">
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-200">Juris-Diction(AI)ry</h1>
            <p className="text-sm text-cyan-400">powered by dwani</p>
          </div>
          <div className="w-16"></div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            {/* Overview */}
            <div className="card bg-[#112240] border border-[#1e2d4a] rounded-xl p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-300">Overview</h2>
              <div className="flex flex-wrap justify-around items-center gap-6">
                <div className="flex flex-col items-center">
                  <div className="circle-progress-container relative w-30 h-30">
                    <svg className="w-full h-full" viewBox="0 0 100 100">
                      <circle className="circle-progress-bg" cx="50" cy="50" r="45" fill="none" stroke="#1e2d4a" strokeWidth="10"></circle>
                      <circle className="circle-progress-bar" cx="50" cy="50" r="45" fill="none" stroke="#3b82f6" strokeWidth="10" strokeLinecap="round" style={{ transformOrigin: '50% 50%', transform: 'rotate(-90deg)', transition: 'stroke-dashoffset 1s ease-in-out', strokeDasharray: 283, strokeDashoffset: dashOffsetImpacted }}></circle>
                    </svg>
                    <div className="circle-progress-text absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
                      <span className="text-3xl font-bold text-blue-400">{impactedClients}</span>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-gray-400 font-medium">TOTAL CLIENTS IMPACTED</p>
                </div>
                <div className="flex flex-col items-center">
                  <div className="circle-progress-container relative w-30 h-30">
                    <svg className="w-full h-full" viewBox="0 0 100 100">
                      <circle className="circle-progress-bg" cx="50" cy="50" r="45" fill="none" stroke="#1e2d4a" strokeWidth="10"></circle>
                      <circle className="circle-progress-bar" cx="50" cy="50" r="45" fill="none" stroke="#10b981" strokeWidth="10" strokeLinecap="round" style={{ transformOrigin: '50% 50%', transform: 'rotate(-90deg)', transition: 'stroke-dashoffset 1s ease-in-out', strokeDasharray: 283, strokeDashoffset: dashOffsetNewRegs }}></circle>
                    </svg>
                    <div className="circle-progress-text absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
                      <span className="text-3xl font-bold text-green-400">{uniqueNewRegs}</span>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-gray-400 font-medium">NEW REGULATIONS</p>
                </div>
                <div className="flex flex-col items-center">
                  <div className="circle-progress-container relative w-30 h-30">
                    <svg className="w-full h-full" viewBox="0 0 100 100">
                      <circle className="circle-progress-bg" cx="50" cy="50" r="45" fill="none" stroke="#1e2d4a" strokeWidth="10"></circle>
                      <circle className="circle-progress-bar" cx="50" cy="50" r="45" fill="none" stroke="#ef4444" strokeWidth="10" strokeLinecap="round" style={{ transformOrigin: '50% 50%', transform: 'rotate(-90deg)', transition: 'stroke-dashoffset 1s ease-in-out', strokeDasharray: 283, strokeDashoffset: dashOffsetUrgency }}></circle>
                    </svg>
                    <div className="circle-progress-text absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
                      <span className={`text-2xl font-bold ${urgencyColor}`}>{urgencyLevel}</span>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-gray-400 font-medium">URGENCY LEVEL</p>
                </div>
              </div>
            </div>

            {/* Affected Client Profiles */}
            <ClientTable clients={clients} />

            {/* Regulatory Feed - Updated */}
            <div className="card bg-[#112240] border border-[#1e2d4a] rounded-xl p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-300">Regulatory Feed</h2>
              <ul className="space-y-3 text-gray-400 text-sm">
                <li><span className="font-semibold text-cyan-400">[Oct 9, 2025] USA:</span> IRS releases tax inflation adjustments for tax year 2026, including amendments from the One Big Beautiful Bill; standard deduction raised to $15,750 for singles and $31,500 for married filing jointly.</li>
                <li><span className="font-semibold text-cyan-400">[Oct 9, 2025] USA:</span> IRS 2025-2026 Priority Guidance Plan outlines key focus areas amid government shutdown impacts.</li>
                <li><span className="font-semibold text-cyan-400">[Oct 10, 2025] USA:</span> Treasury and IRS issue proposed regulations for “No Tax on Tips” provision under OBBBA, allowing deduction up to $25,000 for qualified tips.</li>
                <li><span className="font-semibold text-cyan-400">[Oct 4, 2025] USA:</span> One Big Beautiful Bill Act (passed July 2025) introduces $6,000 deduction for individuals age 65+, effective 2025-2028, plus other Trump Tax Plan changes for 2025 filings.</li>
              </ul>
            </div>
          </div>

          {/* Right Column */}
          <div className="space-y-8">
            <div className="card bg-[#112240] border border-[#1e2d4a] rounded-xl p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-300">Quick Actions</h2>
              <div className="space-y-4">
                <button className="w-full quick-action-button text-left p-4 rounded-lg bg-[#112240] border border-[#1e2d4a] text-[#a8b2d1] transition-all duration-300 hover:bg-[#1e2d4a] hover:text-[#64ffda]">Run New Scan</button>
                <button className="w-full quick-action-button text-left p-4 rounded-lg bg-[#112240] border border-[#1e2d4a] text-[#a8b2d1] transition-all duration-300 hover:bg-[#1e2d4a] hover:text-[#64ffda]">Generate Report</button>
                <button className="w-full quick-action-button text-left p-4 rounded-lg bg-[#112240] border border-[#1e2d4a] text-[#a8b2d1] transition-all duration-300 hover:bg-[#1e2d4a] hover:text-[#64ffda]">Client Database</button>
                <button className="w-full quick-action-button text-left p-4 rounded-lg bg-[#112240] border border-[#1e2d4a] text-[#a8b2d1] transition-all duration-300 hover:bg-[#1e2d4a] hover:text-[#64ffda]">Settings</button>
              </div>
            </div>
            <div className="card bg-[#112240] border border-[#1e2d4a] rounded-xl p-6 text-center text-gray-400">
              <p className="text-sm">USER: <span className="font-semibold text-gray-200">TAX_ADVISOR/USERNAME</span></p>
              <p className="text-xs mt-1">LAST UPDATE: JUST NOW</p>
            </div>
            <div className="hidden sm:block card bg-[#112240] border border-[#1e2d4a] rounded-xl opacity-20" style={{backgroundImage: 'radial-gradient(#64ffda 1px, transparent 1px)', backgroundSize: '15px 15px', minHeight: '200px'}}></div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;