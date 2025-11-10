import React from 'react'

const Header = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">
          AI Scoping Bot
        </h1>
        <span className="text-gray-600">Demo Mode - No Login Required</span>
      </div>
    </header>
  )
}

export default Header