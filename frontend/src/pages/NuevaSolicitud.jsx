import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getErrorMessage, solicitudesApi } from '../api/client.js'

const EMPTY = { order_number: '', address: '', phone: '', email: '' }

export default function NuevaSolicitud() {
  const navigate = useNavigate()
  const [medications, setMedications] = useState([])
  const [medicationId, setMedicationId] = useState('')
  const [extra, setExtra] = useState(EMPTY)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  // Cargar el listado de medicamentos una sola vez al montar el componente
  useEffect(() => {
    solicitudesApi.get('/medications')
      .then(({ data }) => setMedications(data))
      .catch((err) => setError(getErrorMessage(err)))
  }, [])

  // Valor derivado: no se guarda en el estado, se calcula en cada render
  const selected = medications.find((m) => m.id === Number(medicationId))
  const isNoPos = selected && !selected.is_pos

  const onChangeExtra = (e) => setExtra({ ...extra, [e.target.name]: e.target.value })

  const onSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const body = { medication_id: Number(medicationId), ...(isNoPos ? extra : {}) }
      await solicitudesApi.post('/requests', body)
      navigate('/solicitudes', { state: { creada: true } })
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h1>Nueva solicitud</h1>
      {error && <p className="alert error">{error}</p>}
      <form onSubmit={onSubmit}>
        <label>Medicamento
          <select value={medicationId} onChange={(e) => setMedicationId(e.target.value)} required>
            <option value="">— Selecciona un medicamento —</option>
            {medications.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name} {m.is_pos ? '(POS)' : '(NO POS)'}
              </option>
            ))}
          </select>
        </label>

        {selected && (
          <p className={`badge ${isNoPos ? 'badge-warn' : 'badge-ok'}`}>
            {isNoPos
              ? 'Medicamento NO POS: completa la información adicional.'
              : 'Medicamento POS: no requiere información adicional.'}
          </p>
        )}

        {/* Formulario adicional: solo se renderiza para medicamentos NO POS */}
        {isNoPos && (
          <fieldset>
            <legend>Información adicional (NO POS)</legend>
            <label>Número de orden *
              <input name="order_number" value={extra.order_number} onChange={onChangeExtra} required maxLength={100} />
            </label>
            <label>Dirección *
              <input name="address" value={extra.address} onChange={onChangeExtra} required maxLength={100} />
            </label>
            <div className="row">
              <label>Teléfono *
                <input type="tel" name="phone" value={extra.phone} onChange={onChangeExtra} required maxLength={20}
                  pattern="[0-9+\-\s\(\)]{7,20}" title="Solo números, espacios, +, - o paréntesis (mín. 7)" />
              </label>
              <label>Correo electrónico *
                <input type="email" name="email" value={extra.email} onChange={onChangeExtra} required maxLength={100} />
              </label>
            </div>
          </fieldset>
        )}

        <div className="actions">
          <button type="button" className="btn btn-ghost" onClick={() => navigate('/solicitudes')}>Cancelar</button>
          <button className="btn" disabled={loading}>{loading ? 'Enviando…' : 'Crear solicitud'}</button>
        </div>
      </form>
    </div>
  )
}
