import React, { useState } from 'react';
import { AlertCircle, CheckCircle, XCircle, Info, Users } from 'lucide-react';
import FileUploader from '../components/FileUploader';
import ResultsTable from '../components/ResultsTable';

const InvoiceUpload = () => {
  const [uploadResult, setUploadResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [teamId, setTeamId] = useState('');

  // ✅ IMPORTANT: NO API CALL HERE
  // FileUploader already uploads and sends result
  const handleFileUpload = (result) => {
    setLoading(false);
    setUploadResult(result);
  };

  const handleUploadStart = () => {
    setLoading(true);
    setUploadResult(null);
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
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Validation Results
            </h3>
            <p className="text-gray-700 mb-4">{summary.message}</p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold">{summary.total_issues}</div>
                <div className="text-sm text-gray-600">Total Issues</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {summary.severity_breakdown?.high || 0}
                </div>
                <div className="text-sm text-gray-600">Critical</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">
                  {summary.severity_breakdown?.medium || 0}
                </div>
                <div className="text-sm text-gray-600">Medium</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {summary.severity_breakdown?.low || 0}
                </div>
                <div className="text-sm text-gray-600">Low</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderInvoiceData = () => {
    if (!uploadResult || uploadResult.error || !uploadResult.invoice_data) return null;

    const { invoice_data } = uploadResult;

    const mainData = [{
      'Invoice Number': invoice_data.invoice_number || 'N/A',
      Vendor: invoice_data.vendor || 'N/A',
      Date: invoice_data.date || 'N/A',
      Total: invoice_data.total ? `$${invoice_data.total}` : 'N/A',
    }];

    return (
      <>
        <ResultsTable
          data={mainData}
          title="Extracted Invoice Information"
          downloadable
        />

        {invoice_data.line_items?.length > 0 && (
          <ResultsTable
            data={invoice_data.line_items.map(item => ({
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
      <div className="bg-white border-b border-gray-200 pb-6">
        <h1 className="text-3xl font-bold">Invoice Upload & Validation</h1>
        <p className="mt-2 text-gray-600">
          Upload invoice files to extract and validate data.
        </p>
      </div>

      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <Users className="h-5 w-5 text-gray-600" />
          <h3 className="text-lg font-semibold">Team Information</h3>
        </div>

        <input
          type="text"
          value={teamId}
          onChange={(e) => setTeamId(e.target.value)}
          placeholder="Team ID (optional)"
          className="w-full rounded-md border-gray-300"
        />
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Upload Invoice</h3>
        <FileUploader
          onFileUpload={handleFileUpload}
          onUploadStart={handleUploadStart}
          loading={loading}
          teamId={teamId}
        />
      </div>

      {uploadResult?.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <XCircle className="h-5 w-5 text-red-600 inline mr-2" />
          {uploadResult.error}
        </div>
      )}

      {!uploadResult?.error && (
        <>
          {renderValidationResults()}
          {renderInvoiceData()}
        </>
      )}

      {loading && (
        <div className="card text-center py-6">
          Processing invoice...
        </div>
      )}
    </div>
  );
};

export default InvoiceUpload;
