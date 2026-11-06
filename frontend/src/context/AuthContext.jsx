import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { authApi, TOKEN_KEY } from '../api/client.js'

const AuthContext = createContext(null)
const USER_KEY = 'user'

export function AuthProvider({ children }) {
  // Estado inicial leído de localStorage para no perder la sesión al recargar la página
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem(USER_KEY) || 'null'))

  const login = async (email, password) => {
    const { data } = await authApi.post('/auth/login', { email, password })
    localStorage.setItem(TOKEN_KEY, data.access_token)
    localStorage.setItem(USER_KEY, JSON.stringify(data.user))
    setToken(data.access_token)
    setUser(data.user)
  }

  const register = async ({ name, lastname, email, password }) => {
    await authApi.post('/auth/register', { name, lastname, email, password })
  }

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    setToken(null)
    setUser(null)
  }, [])

  // El interceptor de axios emite este evento cuando la API responde 401/403
  useEffect(() => {
    window.addEventListener('auth:logout', logout)
    return () => window.removeEventListener('auth:logout', logout)
  }, [logout])

  return (
    <AuthContext.Provider value={{ token, user, isAuthenticated: !!token, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
