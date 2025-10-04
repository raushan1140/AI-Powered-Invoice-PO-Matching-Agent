import React, { useState } from 'react';
import { API } from '../config/api';
import { AlertCircle, CheckCircle, XCircle, Info, Users } from 'lucide-react';
import FileUploader from '../components/FileUploader';
import ResultsTable from '../components/ResultsTable';

const InvoiceUpload = () => {
  const [uploadResult, setUploadResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [teamId, setTeamId] = useState('');

  const handleFileUpload = async (file) => {
    try {
      setLoading(true);
      setUploadResult(null);

      const formData = new FormData();
      formData.append('file', file);
      if (teamId) formData.append('team_id', teamId);

      const response = await fetch(`${API.INVOICES}/upload`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      setUploadResult(result);
    } catch (error) {
      console.error('Upload error:', error);
      setUploadResult({ error: 'Failed to upload invoice. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const getValidationStatusIcon = (status) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="h-6 w-6 text-green-600" />;
      case 'rejected':
        return <XCircle className="h-6 w-6 text-red-600" />;
      case 'approved_with_warnings':
        return <AlertCircle className="h-6 w-6 text-yellow-600" />;
      case 'no_po_match':
        return <XCircle className="h-6 w-6 text-red-600" />;
      default:
        return <Info className="h-6 w-6 text-gray-600" />;
    }
  };

  const getValidationStatusColor = (status) => {
    switch (status) {
      case 'approved':
        return 'bg-green-50 border-green-200';
      case 'rejected':
        return 'bg-red-50 border-red-200';
      case 'approved_with_warnings':
        return 'bg-yellow-50 border-yellow-200';
      case 'no_po_match':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const renderValidationResults = () => {
    if (!uploadResult || uploadResult.error) return null;

    const { validation_result } = uploadResult;
    const summary = validation_result?.summary;
    if (!summary) return null;

    return (
      <div className={`card border-2 ${getValidationStatusColor(summary.status)}`}>
        <div className="flex items-start space-x-4">
          {getValidationStatusIcon(summary.status)}
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Validation Results</h3>
            <p className="text-gray-700 mb-4">{summary.message}</p>

            {/* Summary Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{summary.total_issues}</div>
                <div className="text-sm text-gray-600">Total Issues</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{summary.severity_breakdown?.high || 0}</div>
                <div className="text-sm text-gray-600">Critical</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">{summary.severity_breakdown?.medium || 0}</div>
                <div className="text-sm text-gray-600">Medium</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{summary.severity_breakdown?.low || 0}</div>
                <div className="text-sm text-gray-600">Low</div>
              </div>
            </div>

            {/* Matches */}
            {validation_result.matches && validation_result.matches.length > 0 && (
              <div className="mb-4">
                <h4 className="text-md font-semibold text-green-700 mb-2">Matching Purchase Orders</h4>
                <div className="space-y-2">
                  {validation_result.matches.map((match, index) => (
                    <div key={index} className="bg-green-100 p-3 rounded-lg">
                      <p className="font-medium">PO: {match.po_id}</p>
                      <p className="text-sm text-gray-600">
                        Match Score: {match.match_score.toFixed(1)}%
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Issues */}
            {validation_result.mismatches && validation_result.mismatches.length > 0 && (
              <div>
                <h4 className="text-md font-semibold text-red-700 mb-2">Issues Found</h4>
                <div className="space-y-2">
                  {validation_result.mismatches.map((issue, index) => (
                    <div
                      key={index}
                      className={`p-3 rounded-lg ${
                        issue.severity === 'high'
                          ? 'bg-red-100'
                          : issue.severity === 'medium'
                          ? 'bg-yellow-100'
                          : 'bg-blue-100'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <p className="font-medium">{issue.message}</p>
                        <span
                          className={`px-2 py-1 rounded text-xs font-medium ${
                            issue.severity === 'high'
                              ? 'bg-red-200 text-red-800'
                              : issue.severity === 'medium'
                              ? 'bg-yellow-200 text-yellow-800'
                              : 'bg-blue-200 text-blue-800'
                          }`}
                        >
                          {issue.severity}
                        </span>
                      </div>
                      {issue.details && (
                        <div className="mt-2 text-sm text-gray-600">
                          <pre className="whitespace-pre-wrap">
                            {JSON.stringify(issue.details, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderInvoiceData = () => {
    if (!uploadResult || uploadResult.error || !uploadResult.invoice_data) return null;

    const { invoice_data } = uploadResult;
    const mainData = [
      {
        'Invoice Number': invoice_data.invoice_number || 'N/A',
        Vendor: invoice_data.vendor || 'N/A',
        Date: invoice_data.date || 'N/A',
        Total: invoice_data.total ? `$${invoice_data.total}` : 'N/A',
      },
    ];

    return (
      <>
        <ResultsTable data={mainData} title="Extracted Invoice Information" downloadable />
        {invoice_data.line_items && invoice_data.line_items.length > 0 && (
          <ResultsTable
            data={invoice_data.line_items.map((item) => ({
              Item: item.item || 'N/A',
              Quantity: item.qty || 0,
              'Unit Price': item.unit_price ? `$${item.unit_price}` : '$0.00',
              Total: item.total ? `$${item.total}` : '$0.00',
            }))}
            title="Line Items"
            downloadable
          />
        )}
      </>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 pb-6">
        <h1 className="text-3xl font-bold text-gray-900">Invoice Upload & Validation</h1>
        <p className="mt-2 text-gray-600">
          Upload invoice files (PDF or images) to automatically extract data and validate against purchase orders.
        </p>
      </div>

      {/* Team ID Input */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <Users className="h-5 w-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Team Information</h3>
        </div>
        <div className="max-w-md">
          <label htmlFor="teamId" className="block text-sm font-medium text-gray-700 mb-2">
            Team ID (optional)
          </label>
          <input
            type="text"
            id="teamId"
            value={teamId}
            onChange={(e) => setTeamId(e.target.value)}
            placeholder="Enter your team ID for scoring"
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          />
          <p className="mt-1 text-sm text-gray-500">
            Enter your team ID to track your score on the leaderboard.
          </p>
        </div>
      </div>

      {/* File Upload */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Invoice</h3>
        <FileUploader onFileUpload={handleFileUpload} loading={loading} teamId={teamId} />
      </div>

      {/* Error Display */}
      {uploadResult && uploadResult.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <XCircle className="h-5 w-5 text-red-600 mr-2" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Upload Error</h3>
              <p className="text-sm text-red-600 mt-1">{uploadResult.error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {uploadResult && !uploadResult.error && (
        <>
          {renderValidationResults()}
          {renderInvoiceData()}
        </>
      )}

      {/* Loading State */}
      {loading && (
        <div className="card">
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            <span className="ml-3 text-gray-600">Processing invoice...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default InvoiceUpload;
