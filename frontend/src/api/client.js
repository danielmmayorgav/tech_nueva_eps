import axios from 'axios'

export const TOKEN_KEY = 'token'

// Cliente para la API de autenticación (no necesita token)
export const authApi = axios.create({
  baseURL: import.meta.env.VITE_AUTH_API_URL,
})

// Cliente para la API de solicitudes (siempre envía el token)
export const solicitudesApi = axios.create({
  baseURL: import.meta.env.VITE_SOLICITUDES_API_URL,
})

// Interceptor de petición: agrega "Authorization: Bearer <token>" automáticamente
solicitudesApi.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Interceptor de respuesta: si el token expiró o es inválido, cierra la sesión
solicitudesApi.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    if (status === 401 || status === 403) {
      window.dispatchEvent(new Event('auth:logout'))
    }
    return Promise.reject(error)
  },
)

// Convierte cualquier error de axios/FastAPI en un mensaje legible
export function getErrorMessage(error) {
  const detail = error.response?.data?.detail
  if (typeof detail === 'string') return detail
  // Errores de validación de Pydantic: lista de { loc, msg }
  if (Array.isArray(detail)) return detail.map((d) => `${d.loc.at(-1)}: ${d.msg}`).join(' · ')
  if (!error.response) return 'No se pudo conectar con el servidor'
  return 'Ocurrió un error inesperado'
}
