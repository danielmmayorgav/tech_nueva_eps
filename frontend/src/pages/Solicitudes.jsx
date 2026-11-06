import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { getErrorMessage, solicitudesApi } from '../api/client.js'

const PAGE_SIZE = 5

export default function Solicitudes() {
  const location = useLocation()
  const [page, setPage] = useState(1)
  const [data, setData] = useState({ items: [], total: 0, pages: 1 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Se vuelve a ejecutar cada vez que cambia "page"
  useEffect(() => {
    setLoading(true)
    solicitudesApi.get('/requests', { params: { page, size: PAGE_SIZE } })
      .then(({ data }) => { setData(data); setError('') })
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false))
  }, [page])

  const fecha = (iso) => new Date(iso).toLocaleString('es-CO') // MySQL guarda la hora local del servidor

  return (
    <div className="card">
      <div className="header-row">
        <h1>Mis solicitudes</h1>
        <Link to="/solicitudes/nueva" className="btn">+ Nueva solicitud</Link>
      </div>

      {location.state?.creada && <p className="alert success">Solicitud creada correctamente.</p>}
      {error && <p className="alert error">{error}</p>}

      {!loading && data.items.length === 0 ? (
        <p className="muted empty">Aún no tienes solicitudes.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>#</th><th>Medicamento</th><th>Tipo</th><th>N.º orden</th>
                <th>Dirección</th><th>Teléfono</th><th>Correo</th><th>Fecha</th>
              </tr>
            </thead>
            <tbody className={loading ? 'loading' : ''}>
              {data.items.map((s) => (
                <tr key={s.id}>
                  <td>{s.id}</td>
                  <td>{s.medication.name}</td>
                  <td>
                    <span className={`badge ${s.medication.is_pos ? 'badge-ok' : 'badge-warn'}`}>
                      {s.medication.is_pos ? 'POS' : 'NO POS'}
                    </span>
                  </td>
                  <td>{s.order_number ?? '—'}</td>
                  <td>{s.address ?? '—'}</td>
                  <td>{s.phone ?? '—'}</td>
                  <td>{s.email ?? '—'}</td>
                  <td>{fecha(s.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="pagination">
        <button className="btn btn-ghost" disabled={page <= 1 || loading} onClick={() => setPage(page - 1)}>
          ← Anterior
        </button>
        <span>Página {data.page ?? page} de {data.pages} · {data.total} solicitudes</span>
        <button className="btn btn-ghost" disabled={page >= data.pages || loading} onClick={() => setPage(page + 1)}>
          Siguiente →
        </button>
      </div>
    </div>
  )
}
