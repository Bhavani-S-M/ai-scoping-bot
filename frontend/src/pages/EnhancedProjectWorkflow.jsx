//frontend/src/pages/EnhancedProjectWorkflow.jsx
import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import axios from '../config/axios'

const EnhancedProjectWorkflow = () => {
  const { projectId } = useParams()
  const [currentStep, setCurrentStep] = useState(1)
  const [project, setProject] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [scope, setScope] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const steps = [
    { id: 1, name: 'Project Info', icon: '📝' },
    { id: 2, name: 'RAG Analysis', icon: '🔍' },
    { id: 3, name: 'Scope Generation', icon: '📊' },
    { id: 4, name: 'Review & Export', icon: '📥' }
  ]

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

  const handleRAGAnalysis = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await axios.post(`/api/projects/${projectId}/analyze-with-rag`)
      setAnalysis(response.data)
      setCurrentStep(2)
    } catch (err) {
      setError('RAG analysis failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateScope = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await axios.post(`/api/projects/${projectId}/generate-scope-with-rag`, {
        answered_questions: analysis?.questions?.map(q => ({
          question_id: q.id,
          question: q.question,
          answer: "User provided answer" // In real app, collect answers from user
        }))
      })
      
      setScope(response.data)
      setCurrentStep(3)
    } catch (err) {
      setError('Scope generation failed: ' + (err.response?.data?.detail || err.message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Progress Steps */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <React.Fragment key={step.id}>
              <div className="flex flex-col items-center">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl ${
                  currentStep >= step.id ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-400'
                }`}>
                  {step.icon}
                </div>
                <span className="mt-2 text-sm font-medium">{step.name}</span>
              </div>
              {index < steps.length - 1 && (
                <div className={`flex-1 h-1 mx-4 ${
                  currentStep > step.id ? 'bg-blue-500' : 'bg-gray-200'
                }`} />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Step 1: Project Info */}
      {currentStep === 1 && project && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold mb-4">Step 1: Project Information</h2>
          
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <h3 className="font-semibold">Project Details</h3>
              <p><strong>Name:</strong> {project.name}</p>
              <p><strong>Domain:</strong> {project.domain}</p>
              <p><strong>Complexity:</strong> {project.complexity}</p>
            </div>
            <div>
              <h3 className="font-semibold">Technical Info</h3>
              <p><strong>Tech Stack:</strong> {project.tech_stack || 'Not specified'}</p>
              <p><strong>Use Cases:</strong> {project.use_cases || 'Not specified'}</p>
            </div>
          </div>

          <button
            onClick={handleRAGAnalysis}
            disabled={loading}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium"
          >
            {loading ? 'Analyzing...' : 'Start RAG Analysis →'}
          </button>
        </div>
      )}

      {/* Step 2: RAG Analysis Results */}
      {currentStep === 2 && analysis && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold mb-4">Step 2: RAG Analysis Results</h2>
          
          {/* Similar Projects */}
          {analysis.similar_projects && analysis.similar_projects.length > 0 && (
            <div className="mb-6">
              <h3 className="text-xl font-semibold mb-3">📊 Similar Historical Projects</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {analysis.similar_projects.map((proj, idx) => (
                  <div key={idx} className="border rounded-lg p-4 bg-blue-50">
                    <h4 className="font-semibold">{proj.project_name}</h4>
                    <p>Domain: {proj.domain} | Complexity: {proj.complexity}</p>
                    <p>Cost: ${proj.total_cost?.toLocaleString()} | Duration: {proj.duration} months</p>
                    <p className="text-sm text-green-600">Similarity: {(proj.similarity_score * 100).toFixed(1)}%</p>
                    {proj.key_insights && (
                      <div className="mt-2">
                        <p className="text-sm font-semibold">Key Insights:</p>
                        <ul className="text-sm list-disc list-inside">
                          {proj.key_insights.map((insight, i) => (
                            <li key={i}>{insight}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Questions */}
          <div className="mb-6">
            <h3 className="text-xl font-semibold mb-3">❓ Clarifying Questions</h3>
            <div className="space-y-4">
              {analysis.questions.map((q, idx) => (
                <div key={q.id} className="border-l-4 border-blue-500 pl-4 py-2">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="bg-gray-200 px-2 py-1 rounded text-sm">
                      {q.category}
                    </span>
                    {q.importance === 'high' && (
                      <span className="bg-red-100 text-red-600 px-2 py-1 rounded text-sm">
                        High Priority
                      </span>
                    )}
                  </div>
                  <p className="font-medium">{q.question}</p>
                  {q.suggested_answers && q.suggested_answers.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {q.suggested_answers.map((answer, i) => (
                        <label key={i} className="flex items-center gap-2">
                          <input type="radio" name={q.id} value={answer} className="w-4 h-4" />
                          <span className="text-sm">{answer}</span>
                        </label>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={handleGenerateScope}
            disabled={loading}
            className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-medium"
          >
            {loading ? 'Generating Scope...' : 'Generate Project Scope →'}
          </button>
        </div>
      )}

      {/* Step 3: Generated Scope */}
      {currentStep === 3 && scope && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold mb-4">Step 3: Generated Project Scope</h2>
          
          {/* RAG Insights */}
          {scope.rag_insights && (
            <div className="mb-6 p-4 bg-green-50 rounded-lg">
              <h3 className="font-semibold text-green-800">🎯 RAG-Enhanced Scope</h3>
              <p>This scope was enhanced using insights from {scope.rag_insights.similar_projects_count} similar historical projects.</p>
              <p>Most similar project: <strong>{scope.rag_insights.most_similar_project}</strong></p>
            </div>
          )}

          {/* Scope Overview */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h3 className="text-xl font-semibold mb-3">📋 Project Overview</h3>
              <p className="mb-4">{scope.overview?.project_summary}</p>
              
              <h4 className="font-semibold mb-2">Key Objectives</h4>
              <ul className="list-disc list-inside space-y-1 mb-4">
                {scope.overview?.key_objectives?.map((obj, idx) => (
                  <li key={idx}>{obj}</li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-3">💰 Cost Summary</h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-2xl font-bold text-green-600">
                  ${scope.cost_breakdown?.total_cost?.toLocaleString()}
                </p>
                <p className="text-sm text-gray-600">Total Project Cost</p>
                {scope.cost_breakdown?.contingency_amount && (
                  <p className="text-sm mt-2">
                    Contingency: ${scope.cost_breakdown.contingency_amount.toLocaleString()} 
                    ({scope.cost_breakdown.contingency_percentage}%)
                  </p>
                )}
              </div>

              <h4 className="font-semibold mt-4 mb-2">📅 Timeline</h4>
              <p>{scope.timeline?.total_duration_months} months total</p>
              
              <div className="mt-2 space-y-2">
                {scope.timeline?.phases?.map((phase, idx) => (
                  <div key={idx} className="flex justify-between text-sm">
                    <span>{phase.phase_name}</span>
                    <span>{phase.duration_weeks} weeks</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Resources Table */}
          <div className="mt-6">
            <h3 className="text-xl font-semibold mb-3">👥 Resource Plan</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left">Role</th>
                    <th className="px-4 py-2 text-right">Count</th>
                    <th className="px-4 py-2 text-right">Effort (months)</th>
                    <th className="px-4 py-2 text-right">Monthly Rate</th>
                    <th className="px-4 py-2 text-right">Total Cost</th>
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
              </table>
            </div>
          </div>

          <div className="mt-6 flex gap-4">
            <button className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium">
              Export as PDF
            </button>
            <button className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-medium">
              Export as Excel
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default EnhancedProjectWorkflow