//frontend/src/pages/Projects.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, Filter } from 'lucide-react';
import api from '../config/axios';

const Projects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newProject, setNewProject] = useState({
    name: '',
    domain: '',
    complexity: 'moderate'
  });

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await api.get('/api/projects');
      setProjects(response.data);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const createProject = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/api/projects', newProject);
      setProjects([...projects, response.data]);
      setShowCreateModal(false);
      setNewProject({ name: '', domain: '', complexity: 'moderate' });
    } catch (error) {
      console.error('Failed to create project:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Projects</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <Plus size={20} />
          New Project
        </button>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((project) => (
          <div key={project.id} className="bg-white rounded-lg shadow border p-6 hover:shadow-md transition-shadow">
            <h3 className="font-semibold text-lg mb-2">{project.name}</h3>
            <div className="space-y-2 text-sm text-gray-600">
              <p><strong>Domain:</strong> {project.domain || 'Not specified'}</p>
              <p><strong>Complexity:</strong> 
                <span className={`ml-2 px-2 py-1 rounded text-xs ${
                  project.complexity === 'complex' ? 'bg-red-100 text-red-800' :
                  project.complexity === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {project.complexity || 'moderate'}
                </span>
              </p>
              <p><strong>Created:</strong> {new Date(project.created_at).toLocaleDateString()}</p>
            </div>
            <div className="mt-4 flex gap-2">
              <Link
                to={`/projects/${project.id}/enhanced-workflow`}
                className="flex-1 bg-blue-500 hover:bg-blue-600 text-white text-center py-2 rounded text-sm"
              >
                Enhanced Workflow
              </Link>
            </div>
          </div>
        ))}
      </div>

      {projects.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-2">No projects yet</h3>
          <p className="text-gray-500 mb-4">Create your first project to get started with AI-powered scoping</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg"
          >
            Create Project
          </button>
        </div>
      )}

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Create New Project</h2>
            <form onSubmit={createProject} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Project Name *
                </label>
                <input
                  type="text"
                  required
                  value={newProject.name}
                  onChange={(e) => setNewProject({...newProject, name: e.target.value})}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  placeholder="Enter project name"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Domain
                </label>
                <input
                  type="text"
                  value={newProject.domain}
                  onChange={(e) => setNewProject({...newProject, domain: e.target.value})}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  placeholder="e.g., Healthcare, Finance, E-commerce"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Complexity
                </label>
                <select
                  value={newProject.complexity}
                  onChange={(e) => setNewProject({...newProject, complexity: e.target.value})}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                >
                  <option value="simple">Simple</option>
                  <option value="moderate">Moderate</option>
                  <option value="complex">Complex</option>
                  <option value="enterprise">Enterprise</option>
                </select>
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 py-2 rounded"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-blue-500 hover:bg-blue-600 text-white py-2 rounded"
                >
                  Create Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Projects;