//frontend/src/pages/EnhancedProjectWorkflow.jsx - ULTIMATE VERSION
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  FileUp, Bot, CheckCircle, Download, MessageCircle, 
  TrendingUp, AlertTriangle, Layers, Users, Clock,
  DollarSign, Eye, EyeOff, RefreshCw, Save, Send, FileText, X
} from 'lucide-react';
import api from '../config/axios';

const EnhancedProjectWorkflow = () => {
  const { projectId } = useParams();
  
  const [scope, setScope] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [refinements, setRefinements] = useState([]);
  
  const [currentStep, setCurrentStep] = useState(1);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [extractedEntities, setExtractedEntities] = useState(null);
  const [showFullScope, setShowFullScope] = useState(false);
  const [isFinalized, setIsFinalized] = useState(false);
  
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  
  const [previewModal, setPreviewModal] = useState({ open: false, type: null });

  const steps = [
    { id: 1, name: 'Upload Document', icon: FileUp },
    { id: 2, name: 'AI Analysis', icon: Bot },
    { id: 3, name: 'Comprehensive Scope', icon: Layers },
    { id: 4, name: 'Real-time Refinement', icon: MessageCircle },
    { id: 5, name: 'Finalize & Export', icon: CheckCircle }
  ];

  // File upload
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadedFile(file);
    setLoading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post(`/api/projects/${projectId}/upload-document`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      console.log('✅ Upload:', response.data);
      setExtractedEntities(response.data.extracted_entities || response.data);
      setCurrentStep(2);
    } catch (error) {
      console.error('❌ Upload error:', error);
      setError('Upload failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  // Generate scope
  const generateScope = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await api.post(`/api/projects/${projectId}/generate-comprehensive-scope`);
      
      console.log('✅ Scope:', response.data);
      
      if (response.data.scope) {
        setScope(response.data.scope);
        setCurrentStep(3);
      } else {
        throw new Error('No scope data');
      }
    } catch (error) {
      console.error('❌ Scope error:', error);
      setError('Failed to generate: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  // Refinement with FORCED UI update
  const handleRefinement = async (message) => {
    if (!message.trim() || !scope) return;

    setLoading(true);
    setError('');
    
    const newHistory = [...chatHistory, { role: 'user', message }];
    setChatHistory(newHistory);
    
    try {
      const response = await api.post('/api/refinement/refine', {
        message,
        current_scope: scope,
        project_id: projectId
      });

      console.log('✅ Refinement:', response.data);

      if (response.data.updated_scope) {
        // ✅ CRITICAL: Force complete re-render
        const newScope = JSON.parse(JSON.stringify(response.data.updated_scope));
        setScope(newScope);
        
        // Force immediate state update
        setTimeout(() => {
          setScope(prev => ({ ...newScope }));
        }, 100);
        
        setChatHistory([...newHistory, {
          role: 'assistant',
          message: response.data.response || 'Scope updated',
          changes: response.data.changes_made || []
        }]);
        
        setRefinements(prev => [...prev, {
          message,
          changes: response.data.changes_made
        }]);
        
        setChatMessage('');
      }
    } catch (error) {
      console.error('❌ Refinement error:', error);
      setError('Refinement failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  // Quick actions
  const handleQuickAction = (action) => {
    const messages = {
      'discount': 'Apply 10% discount to total cost',
      'developer': 'Add 1 more frontend developer',
      'timeline': 'Make timeline 2 weeks shorter',
      'security': 'Add security testing activities'
    };
    handleRefinement(messages[action]);
  };

  // Preview - IMPROVED
  const handlePreview = (type) => {
    if (!scope) return;
    setPreviewModal({ open: true, type });
  };

  // Finalize
  const finalizeScope = async () => {
    setLoading(true);
    try {
      await api.post(`/api/projects/${projectId}/finalize`, {
        scope_data: scope,
        approval_status: 'approved'
      });
      
      setIsFinalized(true);
      setCurrentStep(5);
      console.log('✅ Finalized');
    } catch (error) {
      console.error('❌ Finalize error:', error);
      setError('Finalize failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  // Export - FIXED endpoint
  const handleExport = async (format) => {
    setLoading(true);
    setError('');
    
    try {
      console.log('📥 Exporting:', format);
      
      const response = await api.post(
        '/api/exports/generate',  // ✅ Correct endpoint
        {
          project_id: projectId,
          scope_data: scope,
          format: format
        },
        { 
          responseType: 'blob',
          timeout: 60000
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      const extensions = { pdf: 'pdf', excel: 'xlsx', json: 'json', all: 'zip' };
      const filename = `scope_${Date.now()}.${extensions[format]}`;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      console.log('✅ Exported:', format);
    } catch (error) {
      console.error('❌ Export error:', error);
      setError('Export failed. Make sure backend exports.py line 34 has: router = APIRouter(prefix="/exports")');
    } finally {
      setLoading(false);
    }
  };

  // Progress
  const renderProgressSteps = () => (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const StepIcon = step.icon;
          const isCompleted = currentStep > step.id;
          const isCurrent = currentStep === step.id;
          
          return (
            <React.Fragment key={step.id}>
              <div className="flex flex-col items-center text-center">
                <div className={`w-16 h-16 rounded-full flex items-center justify-center transition-all ${
                  isCompleted ? 'bg-green-500 text-white' :
                  isCurrent ? 'bg-blue-500 text-white ring-4 ring-blue-200' :
                  'bg-gray-200 text-gray-400'
                }`}>
                  <StepIcon size={28} />
                </div>
                <span className="mt-3 text-sm font-medium">{step.name}</span>
              </div>
              {index < steps.length - 1 && (
                <div className={`flex-1 h-2 mx-4 rounded-full ${
                  isCompleted ? 'bg-green-500' : 'bg-gray-200'
                }`} />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );

  // Upload
  const renderDocumentUpload = () => (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-3">
        <FileUp className="text-blue-500" />
        Upload Project Document
      </h2>
      
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-500 transition-colors bg-gray-50">
        <input
          type="file"
          onChange={handleFileUpload}
          accept=".pdf,.docx,.doc,.txt"
          className="hidden"
          id="file-upload"
        />
        <label htmlFor="file-upload" className="cursor-pointer block">
          <FileUp size={64} className="mx-auto text-gray-400 mb-4" />
          <p className="text-xl font-medium mb-2">Click to upload</p>
          <p className="text-gray-500">PDF, DOCX, or TXT</p>
        </label>
      </div>

      {loading && (
        <div className="mt-6 text-center">
          <RefreshCw className="animate-spin h-12 w-12 text-blue-500 mx-auto" />
          <p className="mt-4">Processing...</p>
        </div>
      )}
    </div>
  );

  // Extracted entities WITH DELIVERABLES
  const renderExtractedEntities = () => {
    if (!extractedEntities) return null;
    
    return (
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-3">
          <Bot className="text-green-500" />
          AI Analysis Complete
        </h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="bg-blue-50 p-6 rounded-lg">
            <h3 className="font-semibold text-lg mb-3">📋 Project Details</h3>
            <div className="space-y-2 text-sm">
              <p><strong>Type:</strong> {extractedEntities.project_type || 'N/A'}</p>
              <p><strong>Domain:</strong> {extractedEntities.domain || 'General'}</p>
              <p><strong>Complexity:</strong> <span className="px-2 py-1 rounded text-xs bg-yellow-100">{extractedEntities.complexity || 'moderate'}</span></p>
              <p><strong>Duration:</strong> {extractedEntities.estimated_duration || 'N/A'}</p>
            </div>
          </div>
          
          <div className="bg-green-50 p-6 rounded-lg">
            <h3 className="font-semibold text-lg mb-3">🔧 Technology</h3>
            {extractedEntities.tech_stack && extractedEntities.tech_stack.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {extractedEntities.tech_stack.map((tech, idx) => (
                  <span key={idx} className="bg-white px-2 py-1 rounded text-xs border">{tech}</span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* ✅ DELIVERABLES */}
        {extractedEntities.deliverables && extractedEntities.deliverables.length > 0 && (
          <div className="bg-purple-50 p-6 rounded-lg border border-purple-200 mb-6">
            <h3 className="font-semibold text-lg mb-3 text-purple-800">🎯 Key Deliverables</h3>
            <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {extractedEntities.deliverables.map((item, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <CheckCircle size={16} className="text-green-500 mt-1 flex-shrink-0" />
                  <span className="text-sm">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* ✅ COMPLIANCE */}
        {extractedEntities.compliance_requirements && extractedEntities.compliance_requirements.length > 0 && (
          <div className="bg-yellow-50 p-6 rounded-lg border border-yellow-200 mb-6">
            <h3 className="font-semibold text-lg mb-3">⚖️ Compliance</h3>
            <div className="flex flex-wrap gap-2">
              {extractedEntities.compliance_requirements.map((comp, idx) => (
                <span key={idx} className="bg-white px-3 py-1 rounded-full text-sm border">{comp}</span>
              ))}
            </div>
          </div>
        )}

        <button
          onClick={generateScope}
          disabled={loading}
          className="bg-blue-500 hover:bg-blue-600 text-white px-8 py-4 rounded-lg font-medium disabled:opacity-50 w-full flex items-center justify-center gap-3"
        >
          <TrendingUp size={24} />
          {loading ? 'Generating (30-60s)...' : 'Generate Comprehensive Scope →'}
        </button>
      </div>
    );
  };

  // Scope
  const renderScope = () => {
    if (!scope) return null;

    return (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main - 2 cols */}
        <div className="lg:col-span-2 space-y-6">
          {/* Confidence */}
          <div className="bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-lg p-6">
            <h3 className="text-xl font-semibold">AI Confidence</h3>
            <div className="text-5xl font-bold mt-2">88%</div>
            <p className="text-sm mt-2">{refinements.length} refinement{refinements.length !== 1 ? 's' : ''} applied</p>
          </div>

          {/* Overview */}
          {scope.overview && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">📋 Overview</h2>
              <p className="text-gray-700">{scope.overview.project_summary}</p>
            </div>
          )}

          {/* Resources - KEY FIX: Add key prop to force re-render */}
          {scope.resources && scope.resources.length > 0 && (
            <div key={JSON.stringify(scope.resources)} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold flex items-center gap-2">
                  <Users className="text-blue-500" />
                  Resources & Costs
                </h2>
                <button
                  onClick={() => setShowFullScope(!showFullScope)}
                  className="flex items-center gap-2 text-blue-500 text-sm"
                >
                  {showFullScope ? <EyeOff size={16} /> : <Eye size={16} />}
                  {showFullScope ? 'Hide' : 'Show All'}
                </button>
              </div>
              
              {/* Summary */}
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="bg-blue-50 p-4 rounded-lg text-center">
                  <Users size={24} className="mx-auto text-blue-500 mb-2" />
                  <p className="text-2xl font-bold text-blue-600">{scope.resources.length}</p>
                  <p className="text-sm">Roles</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg text-center">
                  <Clock size={24} className="mx-auto text-green-500 mb-2" />
                  <p className="text-2xl font-bold text-green-600">{scope.timeline?.total_duration_months || 6}</p>
                  <p className="text-sm">Months</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg text-center">
                  <DollarSign size={24} className="mx-auto text-purple-500 mb-2" />
                  <p className="text-2xl font-bold text-purple-600">
                    ${scope.cost_breakdown?.total_cost?.toLocaleString() || 0}
                  </p>
                  <p className="text-sm">Total</p>
                </div>
              </div>

              {/* Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 py-2 text-left">Role</th>
                      <th className="px-3 py-2 text-right">Count</th>
                      <th className="px-3 py-2 text-right">Months</th>
                      <th className="px-3 py-2 text-right">Rate</th>
                      <th className="px-3 py-2 text-right">Total</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {(showFullScope ? scope.resources : scope.resources.slice(0, 5)).map((resource, idx) => (
                      <tr key={`${resource.role}-${idx}-${resource.count}`} className="hover:bg-gray-50">
                        <td className="px-3 py-2">{resource.role}</td>
                        <td className="px-3 py-2 text-right">{resource.count}</td>
                        <td className="px-3 py-2 text-right">{resource.effort_months}</td>
                        <td className="px-3 py-2 text-right">${resource.monthly_rate?.toLocaleString()}</td>
                        <td className="px-3 py-2 text-right font-semibold">${resource.total_cost?.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot className="bg-gray-50 font-bold">
                    <tr>
                      <td colSpan="4" className="px-3 py-2 text-right">TOTAL:</td>
                      <td className="px-3 py-2 text-right">${scope.cost_breakdown?.total_cost?.toLocaleString()}</td>
                    </tr>
                  </tfoot>
                </table>
              </div>
              
              {!showFullScope && scope.resources.length > 5 && (
                <p className="text-sm text-gray-500 mt-2 text-center">
                  + {scope.resources.length - 5} more
                </p>
              )}
            </div>
          )}

          {/* Preview buttons */}
          {currentStep === 3 && !isFinalized && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-semibold mb-3">📄 Preview Scope</h3>
              <div className="grid grid-cols-3 gap-3">
                <button onClick={() => handlePreview('json')} className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-3 rounded-lg text-sm flex items-center justify-center gap-2">
                  <FileText size={18} />
                  JSON
                </button>
                <button onClick={() => handlePreview('pdf')} className="bg-red-500 hover:bg-red-600 text-white px-4 py-3 rounded-lg text-sm flex items-center justify-center gap-2">
                  <Eye size={18} />
                  PDF
                </button>
                <button onClick={() => handlePreview('excel')} className="bg-green-500 hover:bg-green-600 text-white px-4 py-3 rounded-lg text-sm flex items-center justify-center gap-2">
                  <Eye size={18} />
                  Excel
                </button>
              </div>
            </div>
          )}

          {/* Finalize */}
          {currentStep === 3 && !isFinalized && (
            <div className="bg-white rounded-lg shadow p-6">
              <button onClick={finalizeScope} disabled={loading} className="bg-purple-500 hover:bg-purple-600 text-white px-8 py-4 rounded-lg font-medium disabled:opacity-50 w-full flex items-center justify-center gap-3">
                <CheckCircle size={24} />
                {loading ? 'Finalizing...' : '✅ Finalize Scope'}
              </button>
            </div>
          )}

          {/* Export */}
          {isFinalized && currentStep === 5 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">📥 Export Final Scope</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button onClick={() => handleExport('pdf')} disabled={loading} className="bg-red-500 hover:bg-red-600 text-white px-4 py-3 rounded-lg disabled:opacity-50">📄 PDF</button>
                <button onClick={() => handleExport('excel')} disabled={loading} className="bg-green-500 hover:bg-green-600 text-white px-4 py-3 rounded-lg disabled:opacity-50">📊 Excel</button>
                <button onClick={() => handleExport('json')} disabled={loading} className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-3 rounded-lg disabled:opacity-50">🔧 JSON</button>
                <button onClick={() => handleExport('all')} disabled={loading} className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-3 rounded-lg disabled:opacity-50">📦 All</button>
              </div>
            </div>
          )}
        </div>

        {/* Refinement Sidebar */}
        {currentStep >= 3 && !isFinalized && (
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6 sticky top-6">
              <h2 className="text-xl font-bold mb-4">💬 Refine</h2>

              {/* Quick Actions */}
              <div className="mb-4">
                <p className="text-sm font-medium mb-2">Quick:</p>
                <div className="grid grid-cols-2 gap-2">
                  <button onClick={() => handleQuickAction('timeline')} disabled={loading} className="bg-gray-100 hover:bg-gray-200 px-3 py-2 rounded text-sm">⏱️ Shorter</button>
                  <button onClick={() => handleQuickAction('discount')} disabled={loading} className="bg-gray-100 hover:bg-gray-200 px-3 py-2 rounded text-sm">💰 10% off</button>
                  <button onClick={() => handleQuickAction('developer')} disabled={loading} className="bg-gray-100 hover:bg-gray-200 px-3 py-2 rounded text-sm">👨‍💻 +Dev</button>
                  <button onClick={() => handleQuickAction('security')} disabled={loading} className="bg-gray-100 hover:bg-gray-200 px-3 py-2 rounded text-sm">🔒 Security</button>
                </div>
              </div>

              {/* Chat */}
              <div className="mb-4 h-96 overflow-y-auto border rounded p-4 space-y-4 bg-gray-50">
                {chatHistory.length === 0 ? (
                  <div className="text-center text-gray-500 py-8">
                    <MessageCircle size={32} className="mx-auto mb-2 text-gray-400" />
                    <p className="text-sm">Ask to refine!</p>
                  </div>
                ) : (
                  chatHistory.map((msg, idx) => (
                    <div key={idx} className={`p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-50 ml-4' : 'bg-white mr-4 border'}`}>
                      <p className="text-xs font-semibold mb-1">{msg.role === 'user' ? 'You' : '🤖 AI'}</p>
                      <p className="text-sm">{msg.message}</p>
                      {msg.changes && msg.changes.length > 0 && (
                        <div className="mt-2 text-xs text-green-600">
                          <strong>✅ Changes:</strong>
                          <ul className="list-disc list-inside">
                            {msg.changes.map((change, cidx) => (
                              <li key={cidx}>{change}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>

              {/* Input */}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !loading && handleRefinement(chatMessage)}
                  placeholder="Ask..."
                  className="flex-1 border rounded px-3 py-2 text-sm"
                  disabled={loading}
                />
                <button
                  onClick={() => handleRefinement(chatMessage)}
                  disabled={loading || !chatMessage.trim()}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
                >
                  <Send size={18} />
                </button>
              </div>

              {refinements.length > 0 && (
                <p className="text-xs text-gray-500 mt-2">
                  {refinements.length} refinement{refinements.length > 1 ? 's' : ''}
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  // Preview Modal - IMPROVED
  const renderPreviewModal = () => {
    if (!previewModal.open || !scope) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setPreviewModal({ open: false, type: null })}>
        <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
          <div className="p-6 border-b flex items-center justify-between bg-gray-50">
            <h3 className="text-xl font-bold">
              {previewModal.type === 'json' && '🔧 JSON Preview'}
              {previewModal.type === 'pdf' && '📄 PDF Preview'}
              {previewModal.type === 'excel' && '📊 Excel Preview'}
            </h3>
            <button onClick={() => setPreviewModal({ open: false, type: null })} className="text-gray-500 hover:text-gray-700">
              <X size={24} />
            </button>
          </div>
          
          <div className="p-6 overflow-y-auto max-h-[70vh]">
            {previewModal.type === 'json' ? (
              <pre className="bg-gray-900 text-green-400 p-4 rounded text-xs overflow-x-auto font-mono">
                {JSON.stringify(scope, null, 2)}
              </pre>
            ) : (
              <div className="space-y-6">
                <div className="bg-blue-50 p-6 rounded-lg border-l-4 border-blue-500">
                  <h4 className="font-bold text-lg mb-4">
                    {previewModal.type === 'pdf' ? '📄 PDF Document Will Contain:' : '📊 Excel Workbook Will Contain:'}
                  </h4>
                  
                  <div className="space-y-4">
                    <div>
                      <p className="font-semibold mb-2">📋 Overview Section</p>
                      <ul className="text-sm space-y-1 ml-4">
                        <li>• Project name and summary</li>
                        <li>• Key objectives ({scope.overview?.key_objectives?.length || 0})</li>
                        <li>• Success metrics</li>
                      </ul>
                    </div>

                    <div>
                      <p className="font-semibold mb-2">👥 Resource Plan</p>
                      <ul className="text-sm space-y-1 ml-4">
                        <li>• {scope.resources?.length || 0} team members</li>
                        <li>• Detailed cost breakdown</li>
                        <li>• Total: ${scope.cost_breakdown?.total_cost?.toLocaleString() || 0}</li>
                      </ul>
                    </div>

                    <div>
                      <p className="font-semibold mb-2">📅 Timeline</p>
                      <ul className="text-sm space-y-1 ml-4">
                        <li>• {scope.timeline?.total_duration_months || 0} months duration</li>
                        <li>• {scope.timeline?.phases?.length || 0} phases</li>
                        <li>• Detailed milestones</li>
                      </ul>
                    </div>

                    <div>
                      <p className="font-semibold mb-2">📝 Activities</p>
                      <ul className="text-sm space-y-1 ml-4">
                        <li>• {scope.activities?.length || 0} detailed activities</li>
                        <li>• Effort estimates</li>
                        <li>• Dependencies</li>
                      </ul>
                    </div>

                    {previewModal.type === 'excel' && (
                      <div>
                        <p className="font-semibold mb-2">📑 Excel Sheets</p>
                        <ul className="text-sm space-y-1 ml-4">
                          <li>• Overview</li>
                          <li>• Timeline</li>
                          <li>• Activities</li>
                          <li>• Resources & Costs</li>
                          <li>• Risks</li>
                        </ul>
                      </div>
                    )}
                  </div>
                </div>

                <div className="bg-green-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-700">
                    <strong>✅ Ready to export!</strong> Click the export button after finalizing to download the complete {previewModal.type.toUpperCase()} document.
                  </p>
                </div>
              </div>
            )}
          </div>
          
          <div className="p-6 border-t bg-gray-50 flex gap-3">
            <button onClick={() => setPreviewModal({ open: false, type: null })} className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-2 rounded">
              Close
            </button>
            {previewModal.type === 'json' && (
              <button
                onClick={() => {
                  const blob = new Blob([JSON.stringify(scope, null, 2)], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const link = document.createElement('a');
                  link.href = url;
                  link.download = `scope_preview_${Date.now()}.json`;
                  link.click();
                }}
                className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded"
              >
                Download JSON
              </button>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto p-6 bg-gray-50 min-h-screen">
      {renderProgressSteps()}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4 flex items-start gap-2">
          <AlertTriangle size={20} className="flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold">Error:</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {currentStep === 1 && renderDocumentUpload()}
      {currentStep === 2 && renderExtractedEntities()}
      {currentStep >= 3 && renderScope()}
      {renderPreviewModal()}

      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl text-center">
            <RefreshCw className="animate-spin h-12 w-12 text-blue-500 mx-auto mb-4" />
            <p className="text-lg font-medium">Processing...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedProjectWorkflow;