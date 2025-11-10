// frontend/src/contexts/AuthContext.jsx
import React, { createContext, useState, useContext, useEffect } from 'react'
import api from '../config/axios'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('auth_token')
      if (token) {
        const response = await api.get('/api/users/me')
        setUser(response.data)
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      localStorage.removeItem('auth_token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    try {
      console.log('🔐 Attempting login with:', { email })
      
      // Use custom login endpoint with JSON body
      const response = await api.post('/api/auth/login', {
        email: email,
        password: password
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
      })

      console.log('✅ Login response:', response.data)

      const { access_token } = response.data

      if (access_token) {
        localStorage.setItem('auth_token', access_token)
        
        // Update axios default header
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        
        // Get user info
        await checkAuth()
        
        return { success: true }
      } else {
        return { success: false, error: 'No access token received' }
      }
    } catch (error) {
      console.error('❌ Login failed:', error)
      const errorMessage = error.response?.data?.detail || 'Login failed. Please check your credentials.'
      return {
        success: false,
        error: errorMessage
      }
    }
  }

  const logout = async () => {
    try {
      await api.post('/api/auth/jwt/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('auth_token')
      delete api.defaults.headers.common['Authorization']
      setUser(null)
    }
  }

  const value = {
    user,
    login,
    logout,
    loading,
    checkAuth
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}