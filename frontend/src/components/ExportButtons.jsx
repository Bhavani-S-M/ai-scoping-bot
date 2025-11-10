//frontend/src/components/ExportButtons.jsx
import React, { useState } from 'react';
import { Download, FileText, Table, Code, CheckCircle, Send } from 'lucide-react';
import api from '../config/axios';

const ExportButtons = ({ scope, projectId, onFinalize }) => {
  const [exporting, setExporting] = useState(false);
  const [exported, setExported] = useState(false);

  const exportFormats = [
    {
      format: 'pdf',
      label: 'PDF Report',
      icon: FileText,
      description: 'Professional document with diagrams',
      color: 'bg-red-500 hover:bg-red-600'
    },
    {
      format: 'excel',
      label: 'Excel Sheet',
      icon: Table,
      description: 'Editable spreadsheet with calculations',
      color: 'bg-green-500 hover:bg-green-600'
    },
    {
      format: 'json',
      label: 'JSON Data',
      icon: Code,
      description: 'Structured data for integration',
      color: 'bg-blue-500 hover:bg-blue-600'
    }
  ];

  const handleExport = async (format) => {
    setExporting(true);
    try {
      const response = await api.post(`/api/exports/export-project`, {
        project_id: projectId,
        format: format,
        scope_data: scope,
        include_diagrams: true
      }, {
        responseType: 'blob'
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `project-scope-${projectId}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      setExported(true);
    } catch (error) {
      console.error('Export error:', error);
      alert('Export failed. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  const handleFinalize = async () => {
    setExporting(true);
    try {
      await onFinalize();
      setExported(true);
    } catch (error) {
      console.error('Finalization error:', error);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2 flex items-center justify-center gap-2">
          <Download className="text-blue-500" />
          Export & Finalize
        </h2>
        <p className="text-gray-600">
          Export your scope in multiple formats and finalize to update knowledge base
        </p>
      </div>

      {/* Export Buttons */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {exportFormats.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.format}
              onClick={() => handleExport(item.format)}
              disabled={exporting}
              className={`${item.color} text-white p-4 rounded-lg transition-all hover:scale-105 disabled:opacity-50 disabled:hover:scale-100`}
            >
              <Icon size={32} className="mx-auto mb-2" />
              <div className="font-medium">{item.label}</div>
              <div className="text-xs opacity-90 mt-1">{item.description}</div>
            </button>
          );
        })}
      </div>

      {/* Finalize Section */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-6">
        <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
          <CheckCircle className="text-green-500" />
          Finalize Scope
        </h3>
        <p className="text-gray-700 mb-4">
          Finalizing will:
        </p>
        <ul className="list-disc list-inside space-y-1 text-sm text-gray-600 mb-4">
          <li>Store this scope in the knowledge base for future learning</li>
          <li>Notify administrators about the finalized scope</li>
          <li>Make this scope available for similar project recommendations</li>
          <li>Generate learning insights for AI improvements</li>
        </ul>

        <button
          onClick={handleFinalize}
          disabled={exporting || exported}
          className="w-full bg-green-500 hover:bg-green-600 text-white py-3 rounded-lg font-medium disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {exporting ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              Finalizing...
            </>
          ) : exported ? (
            <>
              <CheckCircle size={20} />
              Scope Finalized!
            </>
          ) : (
            <>
              <Send size={20} />
              Finalize & Update Knowledge Base
            </>
          )}
        </button>

        {exported && (
          <div className="mt-3 text-center text-sm text-green-600">
            ✅ Scope finalized successfully! Knowledge base updated.
          </div>
        )}
      </div>

      {/* Admin Notification Preview */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h4 className="font-medium text-yellow-800 mb-2">Admin Notification Preview</h4>
        <p className="text-sm text-yellow-700">
          Upon finalization, admins will be notified via email/webhook about this scope with details including:
          project complexity, total cost, duration, and key technologies used.
        </p>
      </div>
    </div>
  );
};

export default ExportButtons;