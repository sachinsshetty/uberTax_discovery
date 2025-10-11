import { useMemo } from 'react';

const statusClasses = {
  'UNDER REVIEW': 'status-under-review bg-[rgba(251,191,36,0.1)] text-[#fbbf24]',
  'AMENDED': 'status-amended bg-[rgba(239,68,68,0.1)] text-[#ef4444]',
  'MONITORED': 'status-monitored bg-[rgba(59,130,246,0.1)] text-[#3b82f6]',
  'LIVE': 'status-live bg-[rgba(16,185,129,0.1)] text-[#10b981]'
};

function ClientTable({ clients }) {
  const statusClass = (status) => statusClasses[status] || '';

  const tableRows = useMemo(() => 
    clients.length > 0 
      ? clients.map(client => (
          <tr key={client.clientId} className="border-b border-gray-700">
            <td className="px-4 py-3">{client.clientId}</td>
            <td className="px-4 py-3">{client.companyName}</td>
            <td className="px-4 py-3">{client.country}</td>
            <td className="px-4 py-3">{client.newRegulation}</td>
            <td className="px-4 py-3">{new Date(client.deadline).toLocaleDateString('de-DE')}</td>
            <td className="px-4 py-3 text-center">
              <span className={`status-pill inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold uppercase ${statusClass(client.status)}`}>
                {client.status}
              </span>
            </td>
          </tr>
        ))
      : [<tr key="empty"><td colSpan="6" className="text-center p-4">No data found.</td></tr>]
  , [clients]);

  return (
    <div className="card bg-[#112240] border border-[#1e2d4a] rounded-xl p-6">
      <h2 className="text-xl font-semibold mb-4 text-gray-300">Affected Client Profiles</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="text-xs text-gray-400 uppercase border-b border-gray-700">
            <tr>
              <th scope="col" className="px-4 py-3">Client ID</th>
              <th scope="col" className="px-4 py-3">Company Name</th>
              <th scope="col" className="px-4 py-3">Country</th>
              <th scope="col" className="px-4 py-3">New Regulation</th>
              <th scope="col" className="px-4 py-3">Deadline</th>
              <th scope="col" className="px-4 py-3 text-center">Status</th>
            </tr>
          </thead>
          <tbody className="text-gray-300">{tableRows}</tbody>
        </table>
      </div>
    </div>
  );
}

export default ClientTable;