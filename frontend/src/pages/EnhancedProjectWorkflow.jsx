//frontend/src/pages/EnhancedProjectWorkflow.jsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  FileUp, Bot, CheckCircle, Download, MessageCircle, 
  TrendingUp, AlertTriangle, Layers, Users, Clock,
  DollarSign, Eye, EyeOff, RefreshCw, Save
} from 'lucide-react';
import { useScope } from '../contexts/ScopeContext';
import RefinementBar from '../components/RefinementBar';
import ArchitectureDiagram from '../components/ArchitectureDiagram';
import ExportButtons from '../components/ExportButtons';
import api from '../config/axios';

const EnhancedProjectWorkflow = () => {
  const { projectId } = useParams();
  const { 
    scope, setScope, updateScope, loading, setLoading,
    refinements, refinementCount, setError 
  } = useScope();
  
  const [currentStep, setCurrentStep] = useState(1);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [extractedEntities, setExtractedEntities] = useState(null);
  const [showFullScope, setShowFullScope] = useState(false);
  const [activeDiagram, setActiveDiagram] = useState('architecture');

  const steps = [
    { id: 1, name: 'Upload Document', icon: FileUp, description: 'Upload RFP/SOW/Requirements' },
    { id: 2, name: 'AI Analysis', icon: Bot, description: 'Entity extraction & parsing' },
    { id: 3, name: 'Comprehensive Scope', icon: Layers, description: 'AI-generated scope with RAG' },
    { id: 4, name: 'Real-time Refinement', icon: MessageCircle, description: 'Interactive adjustments' },
    { id: 5, name: 'Finalize & Export', icon: CheckCircle, description: 'Export & KB learning' }
  ];

  // Handle file upload and entity extraction
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadedFile(file);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post(`/api/projects/${projectId}/upload-document`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setExtractedEntities(response.data.extracted_entities);
      setCurrentStep(2);
    } catch (error) {
      setError('Failed to upload and process document');
      console.error('Upload error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Generate comprehensive scope
  const generateScope = async () => {
    setLoading(true);
    try {
      const response = await api.post(`/api/projects/${projectId}/generate-comprehensive-scope`);
      setScope(response.data.scope);
      setCurrentStep(3);
    } catch (error) {
      setError('Failed to generate scope');
      console.error('Scope generation error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle scope refinement
  const handleRefinement = async (message) => {
    if (!message.trim() || !scope) return;

    setLoading(true);
    try {
      const response = await api.post('/api/refinement/refine', {
        message,
        current_scope: scope,
        project_id: projectId
      });

      updateScope(
        response.data.updated_scope,
        response.data.changes_made,
        response.data.intent
      );
    } catch (error) {
      setError('Failed to process refinement');
      console.error('Refinement error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Finalize scope and update KB
  const finalizeScope = async () => {
    setLoading(true);
    try {
      await api.post(`/api/projects/${projectId}/finalize`, {
        scope_data: scope,
        approval_status: 'approved',
        user_feedback: 'Scope finalized via enhanced workflow'
      });
      
      setCurrentStep(5);
    } catch (error) {
      setError('Failed to finalize scope');
      console.error('Finalization error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Render progress steps
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
                <div className={`w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 ${
                  isCompleted ? 'bg-green-500 text-white' :
                  isCurrent ? 'bg-blue-500 text-white ring-4 ring-blue-200' :
                  'bg-gray-200 text-gray-400'
                }`}>
                  <StepIcon size={28} />
                </div>
                <span className="mt-3 text-sm font-medium max-w-[100px]">{step.name}</span>
                <span className="text-xs text-gray-500 mt-1 max-w-[100px]">{step.description}</span>
              </div>
              {index < steps.length - 1 && (
                <div className={`flex-1 h-2 mx-4 rounded-full transition-all duration-300 ${
                  isCompleted ? 'bg-green-500' : 'bg-gray-200'
                }`} />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );

  // Render step 1: Document upload
  const renderDocumentUpload = () => (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-3">
        <FileUp className="text-blue-500" />
        Upload Project Document
      </h2>
      <p className="text-gray-600 mb-6 text-lg">
        Upload your RFP, SOW, or requirements document. Our AI will extract key entities and prepare for intelligent scoping.
      </p>
      
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
          <p className="text-xl font-medium mb-2">Click to upload or drag and drop</p>
          <p className="text-gray-500">PDF, DOCX, or TXT (Max 10MB)</p>
          <p className="text-sm text-gray-400 mt-2">
            Supports: Requirements documents, RFPs, SOWs, Project briefs
          </p>
        </label>
      </div>

      {loading && (
        <div className="mt-6 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Extracting entities from document...</p>
        </div>
      )}
    </div>
  );

  // Render step 2: Extracted entities
  const renderExtractedEntities = () => (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-3">
        <Bot className="text-green-500" />
        AI Analysis Complete
      </h2>
      <p className="text-gray-600 mb-6">
        Successfully extracted project information from your document. Review and proceed to generate comprehensive scope.
      </p>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
          <h3 className="font-semibold text-lg mb-3 text-blue-800">📋 Project Details</h3>
          <div className="space-y-2">
            <p><strong>Type:</strong> {extractedEntities.project_type}</p>
            <p><strong>Domain:</strong> {extractedEntities.domain}</p>
            <p><strong>Complexity:</strong> 
              <span className={`ml-2 px-2 py-1 rounded text-xs ${
                extractedEntities.complexity === 'complex' ? 'bg-red-100 text-red-800' :
                extractedEntities.complexity === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                'bg-green-100 text-green-800'
              }`}>
                {extractedEntities.complexity}
              </span>
            </p>
            <p><strong>Duration:</strong> {extractedEntities.estimated_duration}</p>
          </div>
        </div>
        
        <div className="bg-green-50 p-6 rounded-lg border border-green-200">
          <h3 className="font-semibold text-lg mb-3 text-green-800">🔧 Technology & Compliance</h3>
          <div className="space-y-2">
            <p><strong>Tech Stack:</strong> 
              <div className="flex flex-wrap gap-1 mt-1">
                {extractedEntities.tech_stack.map((tech, idx) => (
                  <span key={idx} className="bg-white px-2 py-1 rounded text-xs border">
                    {tech}
                  </span>
                ))}
              </div>
            </p>
            <p><strong>Compliance:</strong> 
              <div className="flex flex-wrap gap-1 mt-1">
                {extractedEntities.compliance_requirements.map((comp, idx) => (
                  <span key={idx} className="bg-white px-2 py-1 rounded text-xs border border-yellow-200">
                    {comp}
                  </span>
                ))}
              </div>
            </p>
          </div>
        </div>
      </div>

      <div className="bg-purple-50 p-6 rounded-lg border border-purple-200 mb-6">
        <h3 className="font-semibold text-lg mb-3 text-purple-800">🎯 Key Deliverables</h3>
        <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {extractedEntities.deliverables.map((item, idx) => (
            <li key={idx} className="flex items-start gap-2">
              <CheckCircle size={16} className="text-green-500 mt-1 flex-shrink-0" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>

      <button
        onClick={generateScope}
        disabled={loading}
        className="bg-blue-500 hover:bg-blue-600 text-white px-8 py-4 rounded-lg font-medium disabled:opacity-50 flex items-center gap-3 text-lg w-full justify-center"
      >
        <TrendingUp size={24} />
        Generate Comprehensive Scope with AI →
      </button>
    </div>
  );

  // Render scope overview section
  const renderScopeOverview = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">📋 Project Overview</h2>
        <button
          onClick={() => setShowFullScope(!showFullScope)}
          className="flex items-center gap-2 text-blue-500 hover:text-blue-600"
        >
          {showFullScope ? <EyeOff size={20} /> : <Eye size={20} />}
          {showFullScope ? 'Hide Details' : 'Show Full Scope'}
        </button>
      </div>
      
      <p className="text-gray-700 mb-4">{scope.overview.project_summary}</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <h3 className="font-semibold mb-2">🎯 Key Objectives</h3>
          <ul className="space-y-2">
            {scope.overview.key_objectives.map((obj, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <CheckCircle size={16} className="text-green-500 mt-1 flex-shrink-0" />
                <span>{obj}</span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="font-semibold mb-2">📊 Success Metrics</h3>
          <ul className="space-y-2">
            {scope.overview.success_metrics.map((metric, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <TrendingUp size={16} className="text-blue-500 mt-1 flex-shrink-0" />
                <span>{metric}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );

  // Render resource and cost summary (default preview)
  const renderResourceSummary = () => (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <Users className="text-blue-500" />
        Resource Plan & Costs
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div className="bg-blue-50 p-4 rounded-lg text-center">
          <Users size={24} className="mx-auto text-blue-500 mb-2" />
          <p className="text-2xl font-bold text-blue-600">{scope.resources.length}</p>
          <p className="text-sm text-gray-600">Roles</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg text-center">
          <Clock size={24} className="mx-auto text-green-500 mb-2" />
          <p className="text-2xl font-bold text-green-600">{scope.timeline.total_duration_months}</p>
          <p className="text-sm text-gray-600">Months</p>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg text-center">
          <DollarSign size={24} className="mx-auto text-purple-500 mb-2" />
          <p className="text-2xl font-bold text-purple-600">
            ${scope.cost_breakdown.total_cost.toLocaleString()}
          </p>
          <p className="text-sm text-gray-600">Total Cost</p>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-3 py-2 text-left">Role</th>
              <th className="px-3 py-2 text-right">Count</th>
              <th className="px-3 py-2 text-right">Months</th>
              <th className="px-3 py-2 text-right">Total Cost</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {scope.resources.slice(0, 5).map((resource, idx) => (
              <tr key={idx} className="hover:bg-gray-50">
                <td className="px-3 py-2">{resource.role}</td>
                <td className="px-3 py-2 text-right">{resource.count}</td>
                <td className="px-3 py-2 text-right">{resource.effort_months}</td>
                <td className="px-3 py-2 text-right font-semibold">
                  ${resource.total_cost.toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {scope.resources.length > 5 && (
        <p className="text-sm text-gray-500 mt-2">
          ... and {scope.resources.length - 5} more roles
        </p>
      )}
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto p-6 bg-gray-50 min-h-screen">
      {renderProgressSteps()}

      {/* Step 1: Document Upload */}
      {currentStep === 1 && renderDocumentUpload()}

      {/* Step 2: Extracted Entities */}
      {currentStep === 2 && extractedEntities && renderExtractedEntities()}

      {/* Steps 3-5: Scope Display with Refinement */}
      {currentStep >= 3 && scope && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Content - 3 columns */}
          <div className="lg:col-span-3 space-y-6">
            {/* Confidence Score */}
            <div className="bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-lg p-6 flex items-center justify-between">
              <div>
                <h3 className="text-xl font-semibold">AI Confidence Score</h3>
                <p className="text-sm opacity-90">
                  Based on {scope.metadata.rag_sources_count} similar projects • 
                  {refinementCount > 0 && ` ${refinementCount} refinement${refinementCount > 1 ? 's' : ''} applied`}
                </p>
              </div>
              <div className="text-5xl font-bold">
                {(scope.metadata.confidence_score * 100).toFixed(0)}%
              </div>
            </div>

            {renderScopeOverview()}
            {renderResourceSummary()}

            {/* Full Scope Details (Collapsible) */}
            {showFullScope && (
              <div className="space-y-6">
                {/* Architecture Diagrams */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-xl font-bold mb-4">🏗️ System Architecture</h2>
                  <ArchitectureDiagram 
                    diagram={scope.diagrams.architecture} 
                    type="architecture"
                  />
                </div>

                {/* Timeline */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-xl font-bold mb-4">📅 Timeline & Milestones</h2>
                  <p className="text-3xl font-bold text-blue-600 mb-6">
                    {scope.timeline.total_duration_months} months
                    <span className="text-lg text-gray-600 ml-2">
                      ({scope.timeline.total_duration_weeks} weeks)
                    </span>
                  </p>
                  
                  <div className="space-y-4">
                    {scope.timeline.phases.map((phase, idx) => (
                      <div key={idx} className="border-l-4 border-blue-500 pl-4 py-3 bg-blue-50 rounded-r-lg">
                        <h3 className="font-semibold text-lg">{phase.phase_name}</h3>
                        <p className="text-sm text-gray-600">
                          {phase.duration_weeks} weeks • Week {phase.start_week} to {phase.end_week}
                        </p>
                        <div className="mt-2">
                          <p className="text-sm font-medium">Milestones:</p>
                          <ul className="text-sm list-disc list-inside mt-1">
                            {phase.milestones.map((milestone, midx) => (
                              <li key={midx}>{milestone}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Full Resource Table */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-xl font-bold mb-4">👥 Detailed Resource Plan</h2>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left">Role</th>
                          <th className="px-4 py-3 text-right">Count</th>
                          <th className="px-4 py-3 text-right">Months</th>
                          <th className="px-4 py-3 text-right">Allocation</th>
                          <th className="px-4 py-3 text-right">Monthly Rate</th>
                          <th className="px-4 py-3 text-right">Total Cost</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y">
                        {scope.resources.map((resource, idx) => (
                          <tr key={idx} className="hover:bg-gray-50">
                            <td className="px-4 py-3 font-medium">{resource.role}</td>
                            <td className="px-4 py-3 text-right">{resource.count}</td>
                            <td className="px-4 py-3 text-right">{resource.effort_months}</td>
                            <td className="px-4 py-3 text-right">{resource.allocation_percentage}%</td>
                            <td className="px-4 py-3 text-right">${resource.monthly_rate.toLocaleString()}</td>
                            <td className="px-4 py-3 text-right font-semibold">
                              ${resource.total_cost.toLocaleString()}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Cost Breakdown */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-xl font-bold mb-4">💰 Cost Breakdown</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="font-semibold mb-3">Cost Summary</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>Subtotal:</span>
                          <span>${scope.cost_breakdown.subtotal?.toLocaleString() || scope.cost_breakdown.total_cost.toLocaleString()}</span>
                        </div>
                        {scope.cost_breakdown.discount_applied > 0 && (
                          <div className="flex justify-between text-red-600">
                            <span>Discount ({scope.cost_breakdown.discount_applied}%):</span>
                            <span>-${(scope.cost_breakdown.subtotal - scope.cost_breakdown.total_cost).toLocaleString()}</span>
                          </div>
                        )}
                        <div className="flex justify-between">
                          <span>Contingency ({scope.cost_breakdown.contingency_percentage}%):</span>
                          <span>${scope.cost_breakdown.contingency_amount.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between border-t pt-2 font-bold text-lg">
                          <span>Total Cost:</span>
                          <span className="text-blue-600">
                            ${scope.cost_breakdown.total_cost.toLocaleString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Assumptions */}
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                  <h3 className="font-semibold mb-3 flex items-center gap-2">
                    <AlertTriangle size={20} className="text-yellow-600" />
                    Key Assumptions & Dependencies
                  </h3>
                  <ul className="list-disc list-inside space-y-2">
                    {scope.assumptions.map((assumption, idx) => (
                      <li key={idx}>{assumption}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Export Section */}
            {currentStep >= 4 && (
              <div className="bg-white rounded-lg shadow p-6">
                <ExportButtons 
                  scope={scope} 
                  projectId={projectId}
                  onFinalize={finalizeScope}
                />
              </div>
            )}
          </div>

          {/* Refinement Sidebar - 1 column */}
          <div className="lg:col-span-1">
            <RefinementBar 
              onRefine={handleRefinement}
              loading={loading}
              refinements={refinements}
              currentStep={currentStep}
              onStepChange={setCurrentStep}
            />
          </div>
        </div>
      )}

      {/* Loading Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl text-center">
            <RefreshCw className="animate-spin h-12 w-12 text-blue-500 mx-auto mb-4" />
            <p className="text-lg font-medium">Processing...</p>
            <p className="text-sm text-gray-600">This may take a few moments</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedProjectWorkflow;