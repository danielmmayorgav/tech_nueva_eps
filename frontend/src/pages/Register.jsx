import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getErrorMessage } from '../api/client.js'
import { useAuth } from '../context/AuthContext.jsx'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', lastname: '', email: '', password: '', confirm: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value })

  // Nombre/apellido: solo letras (incluye tildes, ñ, ü) y espacios.
  // Los caracteres no permitidos se eliminan mientras el usuario escribe o pega.
  const onChangeOnlyLetters = (e) => {
    const value = e.target.value.replace(/[^\p{L} ]/gu, '').replace(/ {2,}/g, ' ')
    setForm({ ...form, [e.target.name]: value })
  }

  const onSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (form.password !== form.confirm) {
      setError('Las contraseñas no coinciden')
      return
    }
    setLoading(true)
    try {
      await register(form)
      navigate('/login', { state: { registered: true } })
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card narrow">
      <h1>Crear cuenta</h1>
      {error && <p className="alert error">{error}</p>}
      <form onSubmit={onSubmit}>
        <label>Nombre
          <input name="name" value={form.name} onChange={onChangeOnlyLetters} required minLength={2} maxLength={100}
            pattern="\s*\p{L}[\p{L} ]*" title="Solo letras y espacios" autoComplete="given-name" autoFocus />
        </label>
        <label>Apellido
          <input name="lastname" value={form.lastname} onChange={onChangeOnlyLetters} required minLength={2} maxLength={100}
            pattern="\s*\p{L}[\p{L} ]*" title="Solo letras y espacios" autoComplete="family-name" />
        </label>
        <label>Correo electrónico
          <input type="email" name="email" value={form.email} onChange={onChange} required maxLength={100} />
        </label>
        <label>Contraseña <small>(mínimo 8 caracteres)</small>
          <input type="password" name="password" value={form.password} onChange={onChange} required minLength={8} maxLength={72} />
        </label>
        <label>Confirmar contraseña
          <input type="password" name="confirm" value={form.confirm} onChange={onChange} required />
        </label>
        <button className="btn" disabled={loading}>{loading ? 'Creando…' : 'Registrarme'}</button>
      </form>
      <p className="muted">¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link></p>
    </div>
  )
}
