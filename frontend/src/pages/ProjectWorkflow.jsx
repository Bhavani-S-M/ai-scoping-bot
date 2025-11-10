// frontend/src/pages/ProjectWorkflow.jsx
import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from '../config/axios'

const ProjectWorkflow = () => {
  const { projectId } = useParams()
  const navigate = useNavigate()
  
  // Workflow state management
  const [currentStep, setCurrentStep] = useState(1)
  const [project, setProject] = useState(null)
  const [questions, setQuestions] = useState([])
  const [answers, setAnswers] = useState({})
  const [scope, setScope] = useState(null)
  const [chatHistory, setChatHistory] = useState([])
  const [chatMessage, setChatMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  const steps = [
    { id: 1, name: 'Project Info', icon: '📝' },
    { id: 2, name: 'Questions', icon: '❓' },
    { id: 3, name: 'Scope Generated', icon: '📊' },
    { id: 4, name: 'Refine', icon: '💬' },
    { id: 5, name: 'Export', icon: '📥' }
  ]

  // Load project data on mount
  useEffect(() => {
    if (projectId) {
      loadProject()
    }
  }, [projectId])

  const loadProject = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}`)
      setProject(response.data)
    } catch (err) {
      setError('Failed to load project')
    }
  }

  // ============================================================================
  // STEP 2: Generate Questions
  // ============================================================================
  
  const handleGenerateQuestions = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await axios.post(`/api/projects/${projectId}/generate-questions`)
      setQuestions(response.data.questions)
      setCurrentStep(2)
    } catch (err) {
      setError('Failed to generate questions: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  const handleAnswerChange = (questionId, answer) => {
    setAnswers({
      ...answers,
      [questionId]: answer
    })
  }

  // ============================================================================
  // STEP 3: Generate Comprehensive Scope
  // ============================================================================
  
  // In frontend/src/pages/ProjectWorkflow.jsx
// Find the handleGenerateScope function (around line 97) and replace it with:

const handleGenerateScope = async () => {
  setLoading(true)
  setError('')
  
  try {
    // Prepare answered questions
    const answeredQuestions = questions
      .filter(q => answers[q.id])
      .map(q => ({
        question_id: q.id,
        question: q.question,
        answer: answers[q.id]
      }))
    
    // FIX: Use the correct endpoint with /api prefix
    const response = await axios.post(
      `/api/projects/${projectId}/generate-scope-with-rag`,  // Changed from /projects/
      { answered_questions: answeredQuestions }
    )
    
    setScope(response.data.scope)  // The response has a 'scope' property
    setCurrentStep(3)
  } catch (err) {
    setError('Failed to generate scope: ' + (err.response?.data?.detail || err.message))
  } finally {
    setLoading(false)
  }
}

  // ============================================================================
  // STEP 4: Chat Refinement
  // ============================================================================
  
  const handleSendMessage = async () => {
    if (!chatMessage.trim() || !scope) return
    
    setLoading(true)
    
    // Add user message to chat
    const newHistory = [
      ...chatHistory,
      { role: 'user', message: chatMessage }
    ]
    setChatHistory(newHistory)
    
    try {
      const response = await axios.post(`/api/projects/${projectId}/chat`, {
        message: chatMessage,
        current_scope: scope
      })
      
      // Update scope and add AI response
      setScope(response.data.updated_scope)
      setChatHistory([
        ...newHistory,
        {
          role: 'assistant',
          message: response.data.response,
          changes: response.data.changes_made
        }
      ])
      setChatMessage('')
    } catch (err) {
      setError('Chat failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  // ============================================================================
  // STEP 5: Export
  // ============================================================================
  
  const handleExport = async (format) => {
    setLoading(true)
    setError('')
    
    try {
      const response = await axios.post(
        '/api/exports/generate',
        {
          project_id: projectId,
          scope_data: scope,
          format: format
        },
        { responseType: 'blob' }
      )
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      
      const extensions = {
        'pdf': 'pdf',
        'excel': 'xlsx',
        'json': 'json',
        'all': 'zip'
      }
      
      link.setAttribute('download', `${project.name}_scope.${extensions[format]}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      setError('Export failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  // ============================================================================
  // RENDER
  // ============================================================================
  
  if (!project) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading project...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Progress Steps */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <React.Fragment key={step.id}>
              <div className="flex flex-col items-center">
                <div
                  className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl ${
                    currentStep >= step.id
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-400'
                  }`}
                >
                  {step.icon}
                </div>
                <span className="mt-2 text-sm font-medium">{step.name}</span>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`flex-1 h-1 mx-4 ${
                    currentStep > step.id ? 'bg-blue-500' : 'bg-gray-200'
                  }`}
                />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Project Header */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h1 className="text-2xl font-bold text-gray-800">{project.name}</h1>
        <div className="mt-2 flex gap-4 text-sm text-gray-600">
          <span>📂 {project.domain}</span>
          <span>⚡ {project.complexity}</span>
          <span>🕐 {project.duration}</span>
        </div>
      </div>

      {/* Step 1: Project Info (Already created, show button to proceed) */}
      {currentStep === 1 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Step 1: Project Information</h2>
          <p className="text-gray-600 mb-6">
            Your project has been created. Click below to generate clarifying questions.
          </p>
          
          <div className="bg-blue-50 p-4 rounded-lg mb-6">
            <h3 className="font-semibold mb-2">Project Details:</h3>
            <ul className="space-y-2 text-sm">
              <li><strong>Domain:</strong> {project.domain}</li>
              <li><strong>Complexity:</strong> {project.complexity}</li>
              <li><strong>Tech Stack:</strong> {project.tech_stack || 'Not specified'}</li>
              <li><strong>Use Cases:</strong> {project.use_cases || 'Not specified'}</li>
            </ul>
          </div>

          <button
            onClick={handleGenerateQuestions}
            disabled={loading}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium disabled:opacity-50"
          >
            {loading ? 'Generating Questions...' : 'Generate Smart Questions →'}
          </button>
        </div>
      )}

      {/* Step 2: Answer Questions */}
      {currentStep === 2 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Step 2: Answer Clarifying Questions</h2>
          <p className="text-gray-600 mb-6">
            Please answer these questions to help us create a comprehensive project scope.
          </p>

          <div className="space-y-6">
            {questions.map((q, index) => (
              <div key={q.id} className="border-b pb-6">
                <div className="flex items-start gap-2">
                  <span className="bg-blue-100 text-blue-600 rounded-full w-8 h-8 flex items-center justify-center font-bold flex-shrink-0">
                    {index + 1}
                  </span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs bg-gray-200 px-2 py-1 rounded">
                        {q.category}
                      </span>
                      {q.importance === 'high' && (
                        <span className="text-xs bg-red-100 text-red-600 px-2 py-1 rounded">
                          High Priority
                        </span>
                      )}
                    </div>
                    <p className="font-medium mb-3">{q.question}</p>
                    
                    {q.suggested_answers && q.suggested_answers.length > 0 ? (
                      <div className="space-y-2">
                        {q.suggested_answers.map((option, idx) => (
                          <label key={idx} className="flex items-center gap-2 cursor-pointer">
                            <input
                              type="radio"
                              name={q.id}
                              value={option}
                              checked={answers[q.id] === option}
                              onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                              className="w-4 h-4"
                            />
                            <span>{option}</span>
                          </label>
                        ))}
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="radio"
                            name={q.id}
                            value="custom"
                            checked={answers[q.id] && !q.suggested_answers.includes(answers[q.id])}
                            onChange={() => handleAnswerChange(q.id, '')}
                            className="w-4 h-4"
                          />
                          <span>Custom answer:</span>
                        </label>
                        {answers[q.id] && !q.suggested_answers.includes(answers[q.id]) && (
                          <input
                            type="text"
                            value={answers[q.id]}
                            onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                            className="w-full border border-gray-300 rounded px-3 py-2 ml-6"
                            placeholder="Enter your custom answer"
                          />
                        )}
                      </div>
                    ) : (
                      <textarea
                        value={answers[q.id] || ''}
                        onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                        className="w-full border border-gray-300 rounded px-3 py-2"
                        rows="3"
                        placeholder="Your answer here..."
                      />
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="flex gap-4 mt-6">
            <button
              onClick={() => setCurrentStep(1)}
              className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium"
            >
              ← Back
            </button>
            <button
              onClick={handleGenerateScope}
              disabled={loading || Object.keys(answers).length === 0}
              className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium disabled:opacity-50"
            >
              {loading ? 'Generating Scope...' : 'Generate Project Scope →'}
            </button>
          </div>
        </div>
      )}

      {/* Step 3 & 4: Scope Display with Chat */}
      {(currentStep === 3 || currentStep === 4) && scope && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Scope Display - 2 columns */}
          <div className="lg:col-span-2 space-y-6">
            {/* Overview */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">📋 Project Overview</h2>
              <p className="text-gray-700 mb-4">{scope.overview?.project_summary}</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold mb-2">Key Objectives</h3>
                  <ul className="list-disc list-inside space-y-1 text-sm">
                    {scope.overview?.key_objectives?.map((obj, idx) => (
                      <li key={idx}>{obj}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Success Metrics</h3>
                  <ul className="list-disc list-inside space-y-1 text-sm">
                    {scope.overview?.success_metrics?.map((metric, idx) => (
                      <li key={idx}>{metric}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Timeline */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">📅 Timeline</h2>
              <div className="mb-4">
                <p className="text-lg font-semibold">
                  Total Duration: {scope.timeline?.total_duration_months} months
                </p>
              </div>
              
              <div className="space-y-3">
                {scope.timeline?.phases?.map((phase, idx) => (
                  <div key={idx} className="border-l-4 border-blue-500 pl-4 py-2">
                    <h3 className="font-semibold">{phase.phase_name}</h3>
                    <p className="text-sm text-gray-600">
                      {phase.duration_weeks} weeks • Week {phase.start_week} to {phase.end_week}
                    </p>
                    <p className="text-sm mt-1">
                      <strong>Milestones:</strong> {phase.milestones?.join(', ')}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Resources & Cost */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">👥 Resources & Costs</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left">Role</th>
                      <th className="px-4 py-2 text-right">Count</th>
                      <th className="px-4 py-2 text-right">Effort (mo)</th>
                      <th className="px-4 py-2 text-right">Rate</th>
                      <th className="px-4 py-2 text-right">Total</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {scope.resources?.map((resource, idx) => (
                      <tr key={idx}>
                        <td className="px-4 py-2">{resource.role}</td>
                        <td className="px-4 py-2 text-right">{resource.count}</td>
                        <td className="px-4 py-2 text-right">{resource.effort_months}</td>
                        <td className="px-4 py-2 text-right">
                          ${resource.monthly_rate?.toLocaleString()}
                        </td>
                        <td className="px-4 py-2 text-right font-semibold">
                          ${resource.total_cost?.toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot className="bg-gray-50 font-bold">
                    <tr>
                      <td colSpan="4" className="px-4 py-2 text-right">TOTAL:</td>
                      <td className="px-4 py-2 text-right">
                        ${scope.cost_breakdown?.total_cost?.toLocaleString()}
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>

            {/* Activities */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">📝 Key Activities</h2>
              <div className="space-y-2">
                {scope.activities?.slice(0, 10).map((activity, idx) => (
                  <div key={idx} className="flex items-start gap-2 p-2 hover:bg-gray-50 rounded">
                    <span className="bg-blue-100 text-blue-600 rounded px-2 py-1 text-xs font-bold">
                      {activity.effort_days}d
                    </span>
                    <div className="flex-1">
                      <p className="font-medium">{activity.name}</p>
                      <p className="text-sm text-gray-600">{activity.phase}</p>
                    </div>
                  </div>
                ))}
                {scope.activities?.length > 10 && (
                  <p className="text-sm text-gray-500 text-center py-2">
                    + {scope.activities.length - 10} more activities
                  </p>
                )}
              </div>
            </div>

            {/* Export Buttons */}
            {currentStep >= 3 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-bold mb-4">📥 Export Options</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <button
                    onClick={() => handleExport('pdf')}
                    disabled={loading}
                    className="bg-red-500 hover:bg-red-600 text-white px-4 py-3 rounded-lg font-medium disabled:opacity-50"
                  >
                    📄 PDF
                  </button>
                  <button
                    onClick={() => handleExport('excel')}
                    disabled={loading}
                    className="bg-green-500 hover:bg-green-600 text-white px-4 py-3 rounded-lg font-medium disabled:opacity-50"
                  >
                    📊 Excel
                  </button>
                  <button
                    onClick={() => handleExport('json')}
                    disabled={loading}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-3 rounded-lg font-medium disabled:opacity-50"
                  >
                    🔧 JSON
                  </button>
                  <button
                    onClick={() => handleExport('all')}
                    disabled={loading}
                    className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-3 rounded-lg font-medium disabled:opacity-50"
                  >
                    📦 All (ZIP)
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Chat Interface - 1 column */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6 sticky top-6">
              <h2 className="text-xl font-bold mb-4">💬 Refine with AI</h2>
              
              <div className="mb-4 h-96 overflow-y-auto border rounded p-4 space-y-4">
                {chatHistory.length === 0 ? (
                  <div className="text-center text-gray-500 py-8">
                    <p className="mb-2">Ask me to refine the scope!</p>
                    <p className="text-sm">Examples:</p>
                    <ul className="text-xs space-y-1 mt-2">
                      <li>"Make the timeline shorter"</li>
                      <li>"Add more security features"</li>
                      <li>"Increase testing activities"</li>
                    </ul>
                  </div>
                ) : (
                  chatHistory.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`${
                        msg.role === 'user'
                          ? 'bg-blue-50 ml-8'
                          : 'bg-gray-50 mr-8'
                      } p-3 rounded-lg`}
                    >
                      <p className="text-sm font-semibold mb-1">
                        {msg.role === 'user' ? 'You' : 'AI Assistant'}
                      </p>
                      <p className="text-sm">{msg.message}</p>
                      {msg.changes && (
                        <div className="mt-2 text-xs text-gray-600">
                          <strong>Changes:</strong>
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

              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask to refine the scope..."
                  className="flex-1 border border-gray-300 rounded px-3 py-2"
                  disabled={loading}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={loading || !chatMessage.trim()}
                  className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded font-medium disabled:opacity-50"
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProjectWorkflow