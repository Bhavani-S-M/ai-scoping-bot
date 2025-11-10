// frontend/src/contexts/AuthContext.jsx
import React, { createContext, useState, useContext, useEffect } from 'react'
import axios from '../config/axios'

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
    const token = localStorage.getItem('access_token')
    if (token) {
      checkAuth()
    } else {
      setLoading(false)
    }
  }, [])

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await axios.get('/api/users/me', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      setUser(response.data)
    } catch (error) {
      console.error('Auth check failed:', error)
      localStorage.removeItem('access_token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    try {
      const formData = new URLSearchParams()
      formData.append('username', email)
      formData.append('password', password)
      
      const response = await axios.post('/api/auth/jwt/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })
      
      const { access_token } = response.data
      
      localStorage.setItem('access_token', access_token)
      
      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      await checkAuth()
      return { success: true }
    } catch (error) {
      console.error('Login failed:', error)
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed. Please check your credentials.'
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    delete axios.defaults.headers.common['Authorization']
    setUser(null)
  }

  const value = {
    user,
    login,
    logout,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}