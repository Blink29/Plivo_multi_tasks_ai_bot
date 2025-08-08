import React, { useState } from 'react';
import { Upload, FileText, Link, X, Loader2 } from 'lucide-react';
import { MarkdownRenderer } from '../markdown-renderer';
import axiosInstance from '../../axios';

export function DocumentSummarization() {
  const [file, setFile] = useState(null);
  const [url, setUrl] = useState('');
  const [inputType, setInputType] = useState('file'); // 'file' or 'url'
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState('');
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const supportedTypes = ['.pdf', '.doc', '.docx', '.txt', '.html', '.csv', '.rtf'];
  const maxFileSize = 50 * 1024 * 1024; // 50MB

  const validateFile = (file) => {
    if (!file) return { isValid: false, error: 'No file selected' };
    
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    if (!supportedTypes.includes(fileExtension)) {
      return {
        isValid: false,
        error: `Unsupported file type. Please use: ${supportedTypes.join(', ')}`
      };
    }

    if (file.size > maxFileSize) {
      return {
        isValid: false,
        error: 'File too large. Maximum size is 50MB.'
      };
    }

    return { isValid: true };
  };

  const validateUrl = (url) => {
    if (!url.trim()) return { isValid: false, error: 'URL is required' };
    
    try {
      new URL(url);
      return { isValid: true };
    } catch {
      return { isValid: false, error: 'Please enter a valid URL' };
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      const validation = validateFile(droppedFile);
      
      if (validation.isValid) {
        setFile(droppedFile);
        setError('');
      } else {
        setError(validation.error);
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      const validation = validateFile(selectedFile);
      
      if (validation.isValid) {
        setFile(selectedFile);
        setError('');
      } else {
        setError(validation.error);
      }
    }
  };

  const handleSubmit = async () => {
    setIsAnalyzing(true);
    setError('');
    setResult('');

    try {
      if (inputType === 'file') {
        if (!file) {
          setError('Please select a file to summarize');
          return;
        }

        const validation = validateFile(file);
        if (!validation.isValid) {
          setError(validation.error);
          return;
        }

        const formData = new FormData();
        formData.append('document', file);

        const response = await axiosInstance.post('/api/summarize-document', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        setResult(response.data.summary);
      } else {
        // URL input
        const validation = validateUrl(url);
        if (!validation.isValid) {
          setError(validation.error);
          return;
        }

        const response = await axiosInstance.post('/api/summarize-document-url', {
          url: url.trim()
        });

        setResult(response.data.summary);
      }
    } catch (err) {
      console.error('Error summarizing document:', err);
      let errorMessage = 'An error occurred while summarizing the document';
      
      if (err.response) {
        // Server responded with error status
        errorMessage = err.response.data?.detail || err.response.statusText || errorMessage;
      } else if (err.request) {
        // Request was made but no response received
        errorMessage = 'Unable to connect to the server. Please check if the backend is running.';
      } else {
        // Something else happened
        errorMessage = err.message || errorMessage;
      }
      
      setError(errorMessage);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setUrl('');
    setResult('');
    setError('');
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Document Summarization
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Upload documents (PDF, DOC, DOCX) or provide URLs to get comprehensive summaries
        </p>
      </div>

      {/* Input Type Selector */}
      <div className="mb-6">
        <div className="flex space-x-4">
          <button
            onClick={() => {
              setInputType('file');
              setUrl('');
              setError('');
            }}
            className={`px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors ${
              inputType === 'file'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            <FileText size={16} />
            <span>Upload File</span>
          </button>
          <button
            onClick={() => {
              setInputType('url');
              setFile(null);
              setError('');
            }}
            className={`px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors ${
              inputType === 'url'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            <Link size={16} />
            <span>Enter URL</span>
          </button>
        </div>
      </div>

      {/* File Upload Section */}
      {inputType === 'file' && (
        <div className="mb-6">
          <input
            type="file"
            accept={supportedTypes.join(',')}
            onChange={handleFileChange}
            className="hidden"
            id="document-file-input"
          />
          <label
            htmlFor="document-file-input"
            className={`block border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
              dragActive
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 hover:bg-gray-50 dark:hover:bg-gray-800'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {file ? (
              <div className="space-y-4">
                <div className="flex items-center justify-center space-x-2">
                  <FileText className="text-blue-500" size={24} />
                  <span className="text-gray-700 dark:text-gray-300 font-medium">
                    {file.name}
                  </span>
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      setFile(null);
                    }}
                    className="text-red-500 hover:text-red-700"
                    type="button"
                  >
                    <X size={20} />
                  </button>
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  File size: {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex justify-center">
                  <Upload className="text-gray-400" size={48} />
                </div>
                <div>
                  <p className="text-lg text-gray-600 dark:text-gray-400 mb-2">
                    Drag and drop your document here, or click to browse files
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Supported formats: {supportedTypes.join(', ')} (Max: 50MB)
                  </p>
                </div>
              </div>
            )}
          </label>
        </div>
      )}

      {/* URL Input Section */}
      {inputType === 'url' && (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Document URL
          </label>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/document.pdf"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
          />
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Enter a direct link to a PDF, DOC, or other supported document
          </p>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="mb-8 flex space-x-4">
        <button
          onClick={handleSubmit}
          disabled={isAnalyzing || (inputType === 'file' && !file) || (inputType === 'url' && !url.trim())}
          className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2 transition-colors"
        >
          {isAnalyzing ? (
            <>
              <Loader2 size={20} className="animate-spin" />
              <span>Summarizing Document...</span>
            </>
          ) : (
            <>
              <FileText size={20} />
              <span>Summarize Document</span>
            </>
          )}
        </button>

        {(file || url || result) && (
          <button
            onClick={resetForm}
            className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
          >
            Reset
          </button>
        )}
      </div>

      {/* Results Section */}
      {result && (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Document Summary
          </h3>
          <div className="prose dark:prose-invert max-w-none">
            <MarkdownRenderer content={result} />
          </div>
        </div>
      )}
    </div>
  );
}
