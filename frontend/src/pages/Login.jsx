import { useState } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { getErrorMessage } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'

export default function Login() {
  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  // Volver a la página que el usuario intentaba abrir antes de ser redirigido
  const destino = location.state?.from?.pathname || '/solicitudes'
  if (isAuthenticated) return <Navigate to={destino} replace />

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  const onSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(form.email, form.password)
      navigate(destino, { replace: true })
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card narrow">
      <h1>Iniciar sesión</h1>
      {location.state?.registered && <p className="alert success">Cuenta creada. Ya puedes ingresar.</p>}
      {error && <p className="alert error">{error}</p>}
      <form onSubmit={onSubmit}>
        <label>Correo electrónico
          <input type="email" name="email" value={form.email} onChange={onChange} required autoFocus />
        </label>
        <label>Contraseña
          <input type="password" name="password" value={form.password} onChange={onChange} required />
        </label>
        <button className="btn" disabled={loading}>{loading ? 'Ingresando…' : 'Ingresar'}</button>
      </form>
      <p className="muted">¿No tienes cuenta? <Link to="/register">Regístrate</Link></p>
    </div>
  )
}
