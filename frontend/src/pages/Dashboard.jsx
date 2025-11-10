//frontend/src/pages/Dashboard.jsx
import React from 'react'

const Dashboard = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-4">
          Welcome to AI Scoping Bot
        </h1>
        <p className="text-gray-600 mb-6">
          Generate intelligent project scopes with AI-powered assistance.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-blue-50 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-800 mb-2">
              Create Project
            </h3>
            <p className="text-blue-600">
              Start a new project scope with AI assistance
            </p>
          </div>
          
          <div className="bg-green-50 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-green-800 mb-2">
              View History
            </h3>
            <p className="text-green-600">
              Access your previous project scopes
            </p>
          </div>
          
          <div className="bg-purple-50 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-purple-800 mb-2">
              Analytics
            </h3>
            <p className="text-purple-600">
              Track your scoping performance
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard