//frontend/src/components/ArchitectureDiagram.jsx
import React, { useState } from 'react';
import { Eye, Code, Download } from 'lucide-react';

const ArchitectureDiagram = ({ diagram, type = 'architecture' }) => {
  const [viewMode, setViewMode] = useState('preview'); // 'preview' or 'code'

  const downloadDiagram = () => {
    const element = document.createElement('a');
    const file = new Blob([diagram.code], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `${type}-diagram.mmd`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="border rounded-lg overflow-hidden">
      <div className="bg-gray-50 px-4 py-2 border-b flex justify-between items-center">
        <span className="font-medium text-gray-700 capitalize">
          {type} Diagram
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode(viewMode === 'preview' ? 'code' : 'preview')}
            className="flex items-center gap-1 px-2 py-1 text-xs bg-white border rounded hover:bg-gray-50"
          >
            {viewMode === 'preview' ? <Code size={14} /> : <Eye size={14} />}
            {viewMode === 'preview' ? 'View Code' : 'View Preview'}
          </button>
          <button
            onClick={downloadDiagram}
            className="flex items-center gap-1 px-2 py-1 text-xs bg-white border rounded hover:bg-gray-50"
          >
            <Download size={14} />
            Download
          </button>
        </div>
      </div>

      <div className="p-4 bg-white">
        {viewMode === 'preview' ? (
          <div className="text-center py-8 bg-gray-50 rounded border">
            <div className="text-gray-500 mb-2">
              🏗️ Architecture Diagram Preview
            </div>
            <p className="text-sm text-gray-600">
              In production, this would render an interactive Mermaid.js diagram
            </p>
            <div className="mt-4 font-mono text-xs bg-white p-4 rounded border text-left max-h-48 overflow-y-auto">
              {diagram.code}
            </div>
          </div>
        ) : (
          <pre className="font-mono text-sm bg-gray-900 text-green-400 p-4 rounded overflow-x-auto max-h-96">
            {diagram.code}
          </pre>
        )}
      </div>
    </div>
  );
};

export default ArchitectureDiagram;