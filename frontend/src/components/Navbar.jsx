import { Link, NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth()

  return (
    <header className="navbar">
      <Link to="/" className="brand">💊 MediSolicitudes</Link>
      {isAuthenticated ? (
        <nav>
          <NavLink to="/solicitudes" end>Mis solicitudes</NavLink>
          <NavLink to="/solicitudes/nueva">Nueva solicitud</NavLink>
          <span className="user">{user?.name} {user?.lastname}</span>
          <button className="btn btn-ghost" onClick={logout}>Salir</button>
        </nav>
      ) : (
        <nav>
          <NavLink to="/login">Ingresar</NavLink>
          <NavLink to="/register">Registrarse</NavLink>
        </nav>
      )}
    </header>
  )
}
