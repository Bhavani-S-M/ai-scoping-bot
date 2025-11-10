//frontend/src/pages/EnhancedProjectWorkflow.jsx
import React, { useState, useEffect } from 'react';
import { FileUp, Bot, CheckCircle, Download, MessageCircle, TrendingUp, AlertTriangle, Layers } from 'lucide-react';

const EnhancedProjectWorkflow = () => {
  const [projectId] = useState('demo-project-123');
  const [currentStep, setCurrentStep] = useState(1);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [extractedEntities, setExtractedEntities] = useState(null);
  const [scope, setScope] = useState(null);
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const steps = [
    { id: 1, name: 'Upload Document', icon: FileUp },
    { id: 2, name: 'AI Analysis', icon: Bot },
    { id: 3, name: 'Comprehensive Scope', icon: Layers },
    { id: 4, name: 'Refine', icon: MessageCircle },
    { id: 5, name: 'Finalize & Export', icon: CheckCircle }
  ];

  // Demo scope data
  const demoScope = {
    overview: {
      project_summary: "Comprehensive web application development for healthcare patient management system with AI-powered diagnostics assistance.",
      key_objectives: [
        "Develop secure patient management platform",
        "Integrate AI diagnostic support",
        "Ensure HIPAA compliance",
        "Enable real-time data synchronization"
      ],
      success_metrics: [
        "95% system uptime",
        "< 2 second page load time",
        "HIPAA compliance certification",
        "Support for 10,000+ concurrent users"
      ]
    },
    timeline: {
      total_duration_months: 6,
      phases: [
        {
          phase_name: "Planning & Requirements",
          duration_weeks: 4,
          start_week: 1,
          end_week: 4,
          milestones: ["Requirements finalized", "Architecture approved", "Security plan ready"]
        },
        {
          phase_name: "Design & Prototyping",
          duration_weeks: 4,
          start_week: 5,
          end_week: 8,
          milestones: ["UI/UX designs approved", "Database schema finalized", "API specifications ready"]
        },
        {
          phase_name: "Development",
          duration_weeks: 12,
          start_week: 9,
          end_week: 20,
          milestones: ["Core features complete", "AI integration done", "Testing environment ready"]
        },
        {
          phase_name: "Testing & QA",
          duration_weeks: 4,
          start_week: 21,
          end_week: 24,
          milestones: ["All tests passed", "Security audit complete", "Performance optimized"]
        }
      ]
    },
    resources: [
      { role: "Project Manager", count: 1, effort_months: 6, monthly_rate: 10000, total_cost: 60000 },
      { role: "Business Analyst", count: 1, effort_months: 3, monthly_rate: 8000, total_cost: 24000 },
      { role: "UI/UX Designer", count: 2, effort_months: 2, monthly_rate: 7000, total_cost: 28000 },
      { role: "Frontend Developer", count: 2, effort_months: 5, monthly_rate: 8000, total_cost: 80000 },
      { role: "Backend Developer", count: 3, effort_months: 5, monthly_rate: 8500, total_cost: 127500 },
      { role: "QA Engineer", count: 2, effort_months: 3, monthly_rate: 7000, total_cost: 42000 },
      { role: "DevOps Engineer", count: 1, effort_months: 4, monthly_rate: 9000, total_cost: 36000 }
    ],
    cost_breakdown: {
      total_cost: 397500,
      contingency_percentage: 15,
      contingency_amount: 59625
    },
    diagrams: {
      architecture: {
        code: `graph TD
    A[Patient/Healthcare Provider] --> B[Web Frontend]
    A --> C[Mobile App]
    B --> D[API Gateway]
    C --> D
    D --> E[Authentication Service]
    D --> F[Patient Management Service]
    D --> G[AI Diagnostic Service]
    F --> H[(PostgreSQL Database)]
    G --> I[ML Model Server]
    G --> J[External Medical APIs]
    D --> K[File Storage S3]
    
    style B fill:#e1f5ff
    style D fill:#fff4e1
    style F fill:#ffe1f5
    style G fill:#e1ffe1`
      },
      workflow: {
        code: `flowchart LR
    A[Requirements] --> B[Design]
    B --> C[Dev: Frontend]
    B --> D[Dev: Backend]
    C --> E[Integration]
    D --> E
    E --> F[Testing]
    F --> G[Deployment]
    G --> H[Monitoring]`
      }
    },
    metadata: {
      confidence_score: 0.87,
      rag_sources_count: 3,
      version: '2.0'
    },
    assumptions: [
      "Client will provide timely feedback and approvals",
      "All required resources will be available as planned",
      "HIPAA compliance requirements are clearly documented",
      "Third-party medical APIs will be available"
    ]
  };

  useEffect(() => {
    // Simulate initial data loading
    if (currentStep >= 3) {
      setScope(demoScope);
    }
  }, [currentStep]);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadedFile(file);
      setLoading(true);
      
      // Simulate entity extraction
      setTimeout(() => {
        setExtractedEntities({
          project_type: "Web Application",
          domain: "Healthcare",
          complexity: "complex",
          deliverables: ["Patient Management System", "AI Diagnostics", "Mobile App"],
          tech_stack: ["React", "Node.js", "PostgreSQL", "TensorFlow"],
          compliance_requirements: ["HIPAA", "GDPR"],
          estimated_duration: "6 months"
        });
        setLoading(false);
        setCurrentStep(2);
      }, 2000);
    }
  };

  const generateScope = () => {
    setLoading(true);
    setTimeout(() => {
      setScope(demoScope);
      setCurrentStep(3);
      setLoading(false);
    }, 1500);
  };

  const handleRefinement = () => {
    if (!chatMessage.trim()) return;
    
    setLoading(true);
    const userMsg = chatMessage;
    setChatMessage('');
    
    // Simulate AI response
    setTimeout(() => {
      const newHistory = [
        ...chatHistory,
        { role: 'user', message: userMsg },
        { 
          role: 'assistant', 
          message: `I've updated the scope based on your request: "${userMsg}"`,
          changes: ['Timeline adjusted', 'Resources optimized', 'Costs recalculated']
        }
      ];
      setChatHistory(newHistory);
      setLoading(false);
    }, 1000);
  };

  const renderMermaidDiagram = (code) => {
    return (
      <div className="bg-white p-4 rounded border">
        <div className="font-mono text-sm whitespace-pre-wrap bg-gray-50 p-4 rounded">
          {code}
        </div>
        <p className="text-xs text-gray-500 mt-2">
          💡 In production, this renders as an interactive diagram
        </p>
      </div>
    );
  };

  return (
    <div className="max-w-7xl mx-auto p-6 bg-gray-50 min-h-screen">
      {/* Progress Steps */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => {
            const StepIcon = step.icon;
            return (
              <React.Fragment key={step.id}>
                <div className="flex flex-col items-center">
                  <div className={`w-14 h-14 rounded-full flex items-center justify-center ${
                    currentStep >= step.id ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-400'
                  } transition-all duration-300`}>
                    <StepIcon size={24} />
                  </div>
                  <span className="mt-2 text-sm font-medium text-center max-w-[80px]">{step.name}</span>
                </div>
                {index < steps.length - 1 && (
                  <div className={`flex-1 h-1 mx-4 ${
                    currentStep > step.id ? 'bg-blue-500' : 'bg-gray-200'
                  } transition-all duration-300`} />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Step 1: Upload Document */}
      {currentStep === 1 && (
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <FileUp className="text-blue-500" />
            Upload Project Document
          </h2>
          <p className="text-gray-600 mb-6">
            Upload your RFP, SOW, or requirements document. Our AI will extract key entities automatically.
          </p>
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-500 transition-colors">
            <input
              type="file"
              onChange={handleFileUpload}
              accept=".pdf,.docx,.doc,.txt"
              className="hidden"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <FileUp size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-lg font-medium mb-2">Click to upload or drag and drop</p>
              <p className="text-sm text-gray-500">PDF, DOCX, or TXT (Max 10MB)</p>
            </label>
          </div>

          {loading && (
            <div className="mt-6 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
              <p className="mt-4 text-gray-600">Extracting entities from document...</p>
            </div>
          )}
        </div>
      )}

      {/* Step 2: Extracted Entities */}
      {currentStep === 2 && extractedEntities && (
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Bot className="text-green-500" />
            Extracted Project Information
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Project Details</h3>
              <p><strong>Type:</strong> {extractedEntities.project_type}</p>
              <p><strong>Domain:</strong> {extractedEntities.domain}</p>
              <p><strong>Complexity:</strong> {extractedEntities.complexity}</p>
              <p><strong>Duration:</strong> {extractedEntities.estimated_duration}</p>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Technology & Compliance</h3>
              <p><strong>Tech Stack:</strong> {extractedEntities.tech_stack.join(', ')}</p>
              <p><strong>Compliance:</strong> {extractedEntities.compliance_requirements.join(', ')}</p>
            </div>
          </div>

          <div className="bg-purple-50 p-4 rounded-lg mb-6">
            <h3 className="font-semibold mb-2">Key Deliverables</h3>
            <ul className="list-disc list-inside">
              {extractedEntities.deliverables.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>

          <button
            onClick={generateScope}
            disabled={loading}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium disabled:opacity-50 flex items-center gap-2"
          >
            <TrendingUp size={20} />
            Generate Comprehensive Scope →
          </button>
        </div>
      )}

      {/* Step 3 & 4: Comprehensive Scope with Chat */}
      {currentStep >= 3 && scope && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Scope Display - 2 columns */}
          <div className="lg:col-span-2 space-y-6">
            {/* Confidence Badge */}
            <div className="bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-lg p-4 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold">AI Confidence Score</h3>
                <p className="text-sm opacity-90">Based on {scope.metadata.rag_sources_count} similar projects</p>
              </div>
              <div className="text-4xl font-bold">{(scope.metadata.confidence_score * 100).toFixed(0)}%</div>
            </div>

            {/* Overview */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">📋 Project Overview</h2>
              <p className="text-gray-700 mb-4">{scope.overview.project_summary}</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold mb-2">Key Objectives</h3>
                  <ul className="space-y-1 text-sm">
                    {scope.overview.key_objectives.map((obj, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <CheckCircle size={16} className="text-green-500 mt-0.5 flex-shrink-0" />
                        <span>{obj}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Success Metrics</h3>
                  <ul className="space-y-1 text-sm">
                    {scope.overview.success_metrics.map((metric, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <TrendingUp size={16} className="text-blue-500 mt-0.5 flex-shrink-0" />
                        <span>{metric}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Architecture Diagram */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">🏗️ System Architecture</h2>
              {renderMermaidDiagram(scope.diagrams.architecture.code)}
            </div>

            {/* Workflow Diagram */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">📊 Project Workflow</h2>
              {renderMermaidDiagram(scope.diagrams.workflow.code)}
            </div>

            {/* Timeline */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">📅 Timeline & Milestones</h2>
              <p className="text-2xl font-bold text-blue-600 mb-4">
                {scope.timeline.total_duration_months} months
              </p>
              
              <div className="space-y-4">
                {scope.timeline.phases.map((phase, idx) => (
                  <div key={idx} className="border-l-4 border-blue-500 pl-4 py-2">
                    <h3 className="font-semibold text-lg">{phase.phase_name}</h3>
                    <p className="text-sm text-gray-600">
                      {phase.duration_weeks} weeks • Week {phase.start_week} to {phase.end_week}
                    </p>
                    <div className="mt-2">
                      <p className="text-sm font-medium">Milestones:</p>
                      <ul className="text-sm list-disc list-inside">
                        {phase.milestones.map((milestone, midx) => (
                          <li key={midx}>{milestone}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Resources & Costs */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">👥 Resources & Costs</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left">Role</th>
                      <th className="px-4 py-2 text-right">Count</th>
                      <th className="px-4 py-2 text-right">Months</th>
                      <th className="px-4 py-2 text-right">Rate</th>
                      <th className="px-4 py-2 text-right">Total</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {scope.resources.map((resource, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-4 py-2">{resource.role}</td>
                        <td className="px-4 py-2 text-right">{resource.count}</td>
                        <td className="px-4 py-2 text-right">{resource.effort_months}</td>
                        <td className="px-4 py-2 text-right">${resource.monthly_rate.toLocaleString()}</td>
                        <td className="px-4 py-2 text-right font-semibold">${resource.total_cost.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot className="bg-blue-50 font-bold">
                    <tr>
                      <td colSpan="4" className="px-4 py-2 text-right">TOTAL:</td>
                      <td className="px-4 py-2 text-right text-blue-600">
                        ${scope.cost_breakdown.total_cost.toLocaleString()}
                      </td>
                    </tr>
                    <tr>
                      <td colSpan="4" className="px-4 py-2 text-right text-sm">Contingency ({scope.cost_breakdown.contingency_percentage}%):</td>
                      <td className="px-4 py-2 text-right text-sm">
                        ${scope.cost_breakdown.contingency_amount.toLocaleString()}
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>

            {/* Assumptions */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <h3 className="font-semibold mb-2 flex items-center gap-2">
                <AlertTriangle size={20} className="text-yellow-600" />
                Key Assumptions
              </h3>
              <ul className="list-disc list-inside space-y-1 text-sm">
                {scope.assumptions.map((assumption, idx) => (
                  <li key={idx}>{assumption}</li>
                ))}
              </ul>
            </div>

            {/* Export Options */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Download size={24} />
                Export Options
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button className="bg-red-500 hover:bg-red-600 text-white px-4 py-3 rounded-lg font-medium flex flex-col items-center gap-2">
                  📄 PDF
                </button>
                <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-3 rounded-lg font-medium flex flex-col items-center gap-2">
                  📊 Excel
                </button>
                <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-3 rounded-lg font-medium flex flex-col items-center gap-2">
                  🔧 JSON
                </button>
                <button className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-3 rounded-lg font-medium flex flex-col items-center gap-2">
                  📦 All (ZIP)
                </button>
              </div>
            </div>
          </div>

          {/* Chat Refinement - 1 column */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6 sticky top-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <MessageCircle className="text-blue-500" />
                Refine with AI
              </h2>
              
              <div className="mb-4 h-96 overflow-y-auto border rounded p-4 space-y-4 bg-gray-50">
                {chatHistory.length === 0 ? (
                  <div className="text-center text-gray-500 py-8">
                    <Bot size={48} className="mx-auto mb-4 text-gray-400" />
                    <p className="mb-2 font-medium">Ask me to refine the scope!</p>
                    <div className="text-xs space-y-1 mt-4 text-left">
                      <p className="font-semibold">Example requests:</p>
                      <p>• "Make the timeline 2 weeks shorter"</p>
                      <p>• "Add security testing activities"</p>
                      <p>• "Apply 10% discount"</p>
                      <p>• "Remove manual testing tasks"</p>
                      <p>• "Add 2 more frontend developers"</p>
                    </div>
                  </div>
                ) : (
                  chatHistory.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`${
                        msg.role === 'user' ? 'bg-blue-50 ml-8' : 'bg-white mr-8 border'
                      } p-3 rounded-lg`}
                    >
                      <p className="text-xs font-semibold mb-1 text-gray-600">
                        {msg.role === 'user' ? '👤 You' : '🤖 AI Assistant'}
                      </p>
                      <p className="text-sm">{msg.message}</p>
                      {msg.changes && (
                        <div className="mt-2 text-xs bg-green-50 p-2 rounded">
                          <strong>Changes:</strong>
                          <ul className="list-disc list-inside mt-1">
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

              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleRefinement()}
                  placeholder="Type your refinement request..."
                  className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm"
                  disabled={loading}
                />
                <button
                  onClick={handleRefinement}
                  disabled={loading || !chatMessage.trim()}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded font-medium disabled:opacity-50"
                >
                  Send
                </button>
              </div>

              <button
                onClick={() => setCurrentStep(5)}
                className="w-full mt-4 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg font-medium flex items-center justify-center gap-2"
              >
                <CheckCircle size={20} />
                Finalize Scope
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedProjectWorkflow;