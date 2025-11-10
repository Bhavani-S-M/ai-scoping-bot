//frontend/src/pages/Projects.jsx
import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from '../config/axios'

const Projects = () => {
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    name: '',
    domain: '',
    complexity: 'medium',
    tech_stack: '',
    use_cases: '',
    duration: '',
    compliance: ''
  })

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      const response = await axios.get('/api/projects')
      setProjects(response.data)
    } catch (err) {
      console.error('Failed to load projects:', err)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await axios.post('/api/projects', formData)
      const projectId = response.data.id

      // Redirect to workflow
      navigate(`/projects/${projectId}/workflow`)
    } catch (err) {
      setError('Failed to create project: ' + (err.response?.data?.detail || err.message))
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const openWorkflow = (projectId) => {
    navigate(`/projects/${projectId}/workflow`)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Projects</h1>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg"
        >
          + New Project
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {showForm && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Create New Project</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Project Name *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  required
                  placeholder="e.g., Mobile Banking App"
                />
              </div>
            
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Domain *
                </label>
                <select
                  name="domain"
                  value={formData.domain}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  required
                >
                  <option value="">Select Domain</option>
                  <option value="Web Development">Web Development</option>
                  <option value="Mobile App">Mobile App</option>
                  <option value="AI/ML">AI/ML</option>
                  <option value="Data Analytics">Data Analytics</option>
                  <option value="Healthcare">Healthcare</option>
                  <option value="Finance">Finance</option>
                  <option value="E-commerce">E-commerce</option>
                  <option value="IoT">IoT</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Complexity *
                </label>
                <select
                  name="complexity"
                  value={formData.complexity}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  required
                >
                  <option value="simple">Simple</option>
                  <option value="medium">Medium</option>
                  <option value="complex">Complex</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Duration
                </label>
                <input
                  type="text"
                  name="duration"
                  value={formData.duration}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  placeholder="e.g., 6 months"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tech Stack
              </label>
              <input
                type="text"
                name="tech_stack"
                value={formData.tech_stack}
                onChange={handleChange}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                placeholder="e.g., React, Node.js, PostgreSQL"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Use Cases / Requirements
              </label>
              <textarea
                name="use_cases"
                value={formData.use_cases}
                onChange={handleChange}
                rows="4"
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                placeholder="Describe the main use cases and requirements..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Compliance Requirements
              </label>
              <input
                type="text"
                name="compliance"
                value={formData.compliance}
                onChange={handleChange}
                className="w-full border border-gray-300 rounded-lg px-3 py-2"
                placeholder="e.g., GDPR, HIPAA, PCI-DSS"
              />
            </div>

            <div className="flex space-x-4">
              <button
                type="submit"
                disabled={loading}
                className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-lg disabled:opacity-50"
              >
                {loading ? 'Creating...' : 'Create Project & Start Scoping'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false)
                  setError('')
                }}
                disabled={loading}
                className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-2 rounded-lg disabled:opacity-50"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Projects list */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Your Projects</h2>
        {projects.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            No projects yet. Create your first project to get started!
          </p>
        ) : (
          <div className="space-y-4">
            {projects.map((project) => (
              <div
                key={project.id}
                className="border border-gray-200 rounded-lg p-4 hover:border-blue-400 transition-colors"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-800">
                      {project.name}
                    </h3>
                    <div className="mt-2 flex gap-4 text-sm text-gray-600">
                      <span>📂 {project.domain}</span>
                      <span>⚡ {project.complexity}</span>
                      {project.duration && <span>🕐 {project.duration}</span>}
                    </div>
                    <p className="mt-2 text-sm text-gray-600">
                      Created: {new Date(project.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => openWorkflow(project.id)}
                      className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm"
                    >
                      Open Workflow →
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Projects