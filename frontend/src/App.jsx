import { Navigate, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import ProtectedRoute from './components/ProtectedRoute.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import NuevaSolicitud from './pages/NuevaSolicitud.jsx'
import Solicitudes from './pages/Solicitudes.jsx'

export default function App() {
  return (
    <>
      <Navbar />
      <main className="container">
        <Routes>
          {/* Rutas públicas */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Rutas privadas: solo con sesión iniciada */}
          <Route element={<ProtectedRoute />}>
            <Route path="/solicitudes" element={<Solicitudes />} />
            <Route path="/solicitudes/nueva" element={<NuevaSolicitud />} />
          </Route>

          <Route path="*" element={<Navigate to="/solicitudes" replace />} />
        </Routes>
      </main>
    </>
  )
}
