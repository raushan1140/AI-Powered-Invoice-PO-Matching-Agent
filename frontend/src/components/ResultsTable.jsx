import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Download, Eye, EyeOff } from 'lucide-react';

const ResultsTable = ({ data, title, downloadable = false, collapsible = false }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [showFullData, setShowFullData] = useState(false);

  if (!data || data.length === 0) {
    return (
      <div className="card">
        <div className="text-center py-8 text-gray-500">
          <p>No data to display</p>
        </div>
      </div>
    );
  }

  const columns = Object.keys(data[0]);
  const displayData = showFullData ? data : data.slice(0, 10);

  const downloadCSV = () => {
    const headers = columns.join(',');
    const rows = data.map(row => 
      columns.map(col => {
        const value = row[col];
        // Handle values that might contain commas or quotes
        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      }).join(',')
    );
    
    const csvContent = [headers, ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.replace(/\s+/g, '_').toLowerCase()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const formatValue = (value) => {
    if (value === null || value === undefined) return '-';
    if (typeof value === 'number') {
      // Format numbers with proper decimals
      if (value % 1 !== 0) {
        return value.toFixed(2);
      }
      return value.toLocaleString();
    }
    if (typeof value === 'string' && value.length > 50) {
      return (
        <span title={value}>
          {value.substring(0, 50)}...
        </span>
      );
    }
    return value;
  };

  const getStatusBadge = (status) => {
    const statusClasses = {
      'approved': 'status-approved',
      'rejected': 'status-rejected',
      'pending': 'status-pending',
      'approved_with_warnings': 'status-warning',
      'no_po_match': 'status-rejected'
    };
    
    const className = statusClasses[status] || 'bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-sm font-medium';
    
    return <span className={className}>{status}</span>;
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          {collapsible && (
            <button
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="text-gray-400 hover:text-gray-600"
            >
              {isCollapsed ? <ChevronDown className="h-5 w-5" /> : <ChevronUp className="h-5 w-5" />}
            </button>
          )}
        </div>
        <div className="flex items-center space-x-2">
          {data.length > 10 && (
            <button
              onClick={() => setShowFullData(!showFullData)}
              className="btn-secondary text-sm"
            >
              {showFullData ? <EyeOff className="h-4 w-4 mr-1" /> : <Eye className="h-4 w-4 mr-1" />}
              {showFullData ? 'Show Less' : `Show All (${data.length})`}
            </button>
          )}
          {downloadable && (
            <button
              onClick={downloadCSV}
              className="btn-secondary text-sm"
            >
              <Download className="h-4 w-4 mr-1" />
              Download CSV
            </button>
          )}
        </div>
      </div>

      {!isCollapsed && (
        <>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {columns.map((column) => (
                    <th
                      key={column}
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {column.replace(/_/g, ' ')}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {displayData.map((row, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    {columns.map((column) => (
                      <td key={column} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {column === 'status' ? 
                          getStatusBadge(row[column]) : 
                          formatValue(row[column])
                        }
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {data.length > 10 && !showFullData && (
            <div className="mt-4 text-center">
              <p className="text-sm text-gray-500">
                Showing 10 of {data.length} rows
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ResultsTable;
