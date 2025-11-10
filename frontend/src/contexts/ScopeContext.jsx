//frontend/src/contexts/ScopeContext.jsx
import React, { createContext, useContext, useReducer } from 'react'

const ScopeContext = createContext()

const scopeReducer = (state, action) => {
  switch (action.type) {
    case 'SET_SCOPE':
      return {
        ...state,
        scope: action.payload,
        originalScope: action.payload,
        refinements: []
      }
    
    case 'UPDATE_SCOPE':
      const newRefinement = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        changes: action.payload.changes,
        intent: action.payload.intent,
        previousScope: state.scope,
        newScope: action.payload.updatedScope
      }
      
      return {
        ...state,
        scope: action.payload.updatedScope,
        refinements: [...state.refinements, newRefinement],
        refinementCount: state.refinementCount + 1
      }
    
    case 'RESET_SCOPE':
      return {
        ...state,
        scope: state.originalScope,
        refinements: []
      }
    
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload
      }
    
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload
      }
    
    case 'SET_EXPORT_DATA':
      return {
        ...state,
        exportData: action.payload
      }
    
    default:
      return state
  }
}

const initialState = {
  scope: null,
  originalScope: null,
  refinements: [],
  refinementCount: 0,
  loading: false,
  error: null,
  exportData: null
}

export const ScopeProvider = ({ children }) => {
  const [state, dispatch] = useReducer(scopeReducer, initialState)

  const setScope = (scope) => {
    dispatch({ type: 'SET_SCOPE', payload: scope })
  }

  const updateScope = (updatedScope, changes, intent) => {
    dispatch({ 
      type: 'UPDATE_SCOPE', 
      payload: { updatedScope, changes, intent } 
    })
  }

  const resetScope = () => {
    dispatch({ type: 'RESET_SCOPE' })
  }

  const setLoading = (loading) => {
    dispatch({ type: 'SET_LOADING', payload: loading })
  }

  const setError = (error) => {
    dispatch({ type: 'SET_ERROR', payload: error })
  }

  const setExportData = (exportData) => {
    dispatch({ type: 'SET_EXPORT_DATA', payload: exportData })
  }

  const value = {
    ...state,
    setScope,
    updateScope,
    resetScope,
    setLoading,
    setError,
    setExportData
  }

  return (
    <ScopeContext.Provider value={value}>
      {children}
    </ScopeContext.Provider>
  )
}

export const useScope = () => {
  const context = useContext(ScopeContext)
  if (!context) {
    throw new Error('useScope must be used within a ScopeProvider')
  }
  return context
}