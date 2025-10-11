import React from 'react';
import { useState, useEffect } from 'react';
import ClientTable from './components/ClientTable.jsx';

function App() {
  const [clients, setClients] = useState([]);

  useEffect(() => {
    fetch('/api/clients')
      .then(res => res.json())
      .then(data => setClients(data))
      .catch(err => console.error('Error fetching clients:', err));
  }, []);

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
                      <circle className="circle-progress-bar" cx="50" cy="50" r="45" fill="none" stroke="#3b82f6" strokeWidth="10" strokeLinecap="round" style={{ transformOrigin: '50% 50%', transform: 'rotate(-90deg)', transition: 'stroke-dashoffset 1s ease-in-out', strokeDasharray: 283, strokeDashoffset: 85 }}></circle>
                    </svg>
                    <div className="circle-progress-text absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
                      <span className="text-3xl font-bold text-blue-400">124</span>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-gray-400 font-medium">TOTAL CLIENTS IMPACTED</p>
                </div>
                <div className="flex flex-col items-center">
                  <div className="circle-progress-container relative w-30 h-30">
                    <svg className="w-full h-full" viewBox="0 0 100 100">
                      <circle className="circle-progress-bg" cx="50" cy="50" r="45" fill="none" stroke="#1e2d4a" strokeWidth="10"></circle>
                      <circle className="circle-progress-bar" cx="50" cy="50" r="45" fill="none" stroke="#10b981" strokeWidth="10" strokeLinecap="round" style={{ transformOrigin: '50% 50%', transform: 'rotate(-90deg)', transition: 'stroke-dashoffset 1s ease-in-out', strokeDasharray: 283, strokeDashoffset: 212 }}></circle>
                    </svg>
                    <div className="circle-progress-text absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
                      <span className="text-3xl font-bold text-green-400">17</span>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-gray-400 font-medium">NEW REGULATIONS</p>
                </div>
                <div className="flex flex-col items-center">
                  <div className="circle-progress-container relative w-30 h-30">
                    <svg className="w-full h-full" viewBox="0 0 100 100">
                      <circle className="circle-progress-bg" cx="50" cy="50" r="45" fill="none" stroke="#1e2d4a" strokeWidth="10"></circle>
                      <circle className="circle-progress-bar" cx="50" cy="50" r="45" fill="none" stroke="#ef4444" strokeWidth="10" strokeLinecap="round" style={{ transformOrigin: '50% 50%', transform: 'rotate(-90deg)', transition: 'stroke-dashoffset 1s ease-in-out', strokeDasharray: 283, strokeDashoffset: 56 }}></circle>
                    </svg>
                    <div className="circle-progress-text absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
                      <span className="text-2xl font-bold text-red-500">HIGH</span>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-gray-400 font-medium">URGENCY LEVEL</p>
                </div>
              </div>
            </div>

            {/* Affected Client Profiles */}
            <ClientTable clients={clients} />

            {/* Regulatory Feed */}
            <div className="card bg-[#112240] border border-[#1e2d4a] rounded-xl p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-300">Regulatory Feed</h2>
              <ul className="space-y-3 text-gray-400 text-sm">
                <li><span className="font-semibold text-cyan-400">[10:30 AM] Germany:</span> Parliament approves Digital Tax Act 2025.</li>
                <li><span className="font-semibold text-cyan-400">[10:00 AM] USA:</span> Treasury releases new BEAT regulations draft.</li>
                <li><span className="font-semibold text-cyan-400">[9:45 AM] EU:</span> New environmental tax directives proposed.</li>
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