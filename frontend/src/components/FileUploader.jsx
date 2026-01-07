import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, AlertCircle, CheckCircle } from 'lucide-react';
import { API } from '../config/api';


const FileUploader = ({ onFileUpload, loading, teamId }) => {
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploadedFile(file);
    setUploadStatus('uploading');

    try {
      const formData = new FormData();
      formData.append('file', file);
      if (teamId) {
        formData.append('team_id', teamId);
      }

      const response = await fetch(`${API.INVOICES}/upload`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setUploadStatus('success');
        onFileUpload(result);
      } else {
        setUploadStatus('error');
        onFileUpload({ error: result.error || 'Upload failed' });
      }
    } catch (error) {
      setUploadStatus('error');
      onFileUpload({ error: error.message });
    }
  }, [onFileUpload, teamId]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']
    },
    maxFiles: 1,
    disabled: loading
  });

  const removeFile = () => {
    setUploadedFile(null);
    setUploadStatus(null);
  };

  const getStatusIcon = () => {
    switch (uploadStatus) {
      case 'uploading':
        return <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>;
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      default:
        return null;
    }
  };

  const getStatusText = () => {
    switch (uploadStatus) {
      case 'uploading':
        return 'Processing...';
      case 'success':
        return 'Upload successful';
      case 'error':
        return 'Upload failed';
      default:
        return '';
    }
  };

  return (
    <div className="w-full">
      {!uploadedFile ? (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
            ${isDragActive
              ? 'border-primary-400 bg-primary-50'
              : 'border-gray-300 hover:border-gray-400'
            }
            ${loading ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          {isDragActive ? (
            <p className="text-lg text-primary-600">Drop the invoice here...</p>
          ) : (
            <>
              <p className="text-lg text-gray-600 mb-2">
                Drag & drop an invoice file here, or click to select
              </p>
              <p className="text-sm text-gray-500">
                Supports PDF, PNG, JPG, JPEG, TIFF, BMP (max 16MB)
              </p>
            </>
          )}
        </div>
      ) : (
        <div className="border border-gray-300 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <File className="h-8 w-8 text-gray-400" />
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {uploadedFile.name}
                </p>
                <p className="text-sm text-gray-500">
                  {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              {getStatusIcon()}
              <span className="text-sm text-gray-600">{getStatusText()}</span>
              {!loading && (
                <button
                  onClick={removeFile}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="h-5 w-5" />
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {uploadStatus === 'error' && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
            <p className="text-sm text-red-600">
              Upload failed. Please try again with a valid invoice file.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUploader;
