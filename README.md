# Solicitudes de Medicamentos — Prueba Técnica

Aplicación fullstack con **dos APIs independientes en Python (FastAPI)** y un **frontend en React (Vite)**, sobre **MySQL / MariaDB**.

| Componente        | Tecnología                         | Puerto |
|-------------------|------------------------------------|--------|
| `auth_api`        | FastAPI · SQLAlchemy · bcrypt · JWT | 8001   |
| `solicitudes_api` | FastAPI · SQLAlchemy · JWT          | 8002   |
| `frontend`        | React 18 · React Router · Axios     | 5173   |
| `db`              | MySQL 8.4 (`tech_nueva_eps`)        | 3306   |

## Configuración: `.env`
Toda la configuración (base de datos, ambas APIs y frontend) se realiza en **un solo archivo `.env` en la raíz**:
```bash
copy .env.example .env      # y cambiar las claves (DB_PASSWORD, DB_ROOT_PASSWORD, SECRET_KEY)
```
> `SECRET_KEY` es compartida: `auth_api` firma el token y `solicitudes_api` lo verifica con la misma clave.

## Docker Compose
Requisito: Docker Desktop. Un solo comando levanta MySQL, las dos APIs y el frontend:
```bash
docker compose up -d --build
```
| Servicio | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Auth API (Swagger) | http://localhost:8001/docs |
| Solicitudes API (Swagger) | http://localhost:8002/docs |
| MySQL | `localhost:${DB_EXPOSED_PORT}` (3306 por defecto), usuario `DB_USER` |

- La primera vez, MySQL ejecuta `database/schema.sql` automáticamente (tablas + medicamentos de ejemplo). Los datos se conservan en el volumen `db_data`.
- Las APIs esperan a que MySQL esté listo (healthcheck) antes de arrancar.
- Dentro de Docker, `DB_HOST`/`DB_PORT` apuntan al contenedor `db`.

Comandos útiles:
```bash
docker compose logs -f auth_api solicitudes_api   # ver logs
docker compose down                               # detener (conserva los datos)
docker compose down -v                            # detener y BORRAR la base (vuelve a cargar schema.sql)
docker compose up -d --build frontend             # recompilar el frontend tras cambiar VITE_* en el .env
```
Si el puerto 3306 ya está ocupado por un MySQL local, cambiar `DB_EXPOSED_PORT` en el `.env`.

## Tests
Cada API tiene sus propios tests (pytest). Corren contra SQLite en memoria, así que **no necesitan MySQL** y no modifican la base real.
```bash
cd auth_api            # o solicitudes_api
pip install -r requirements-dev.txt
pytest
```
| API | Tests | Qué cubren |
|---|---|---|
| `auth_api` | 28 | Registro (hash bcrypt, email duplicado, nombre solo letras, validaciones), login (JWT válido, credenciales inválidas sin revelar qué falló), manejo de errores |
| `solicitudes_api` | 41 | Token ausente/inválido/expirado, regla POS / NO POS y sus campos obligatorios, formatos, paginación, aislamiento entre usuarios |

## Logs y manejo de errores
- Cada petición queda registrada: `POST /requests -> 201 (35 ms)`. Nivel configurable con `LOG_LEVEL` en el `.env`.
- Eventos de negocio: registro, login exitoso/fallido (sin registrar contraseñas), solicitud creada.
- Los errores de base de datos se traducen a respuestas claras sin exponer SQL ni datos internos:

| Error | HTTP | Ejemplo |
|---|---|---|
| `IntegrityError` | 409 | Restricción única o llave foránea violada |
| `DataError` | 422 | Valor demasiado largo o fuera de rango |
| `OperationalError` | 503 | MySQL |
| Cualquier otro | 500 | Error inesperado (la traza completa queda en el log) |

## Endpoints

### Auth API (8001)
| Método | Ruta             | Descripción                          |
|--------|------------------|--------------------------------------|
| POST   | `/auth/register` | Crea usuario (`name`, `lastname`, `email`, `password` con bcrypt) |
| POST   | `/auth/login`    | Devuelve `access_token` JWT          |

### Solicitudes API (8002) — requieren `Authorization: Bearer <token>`
| Método | Ruta                          | Descripción                                   |
|--------|-------------------------------|-----------------------------------------------|
| GET    | `/medications`                | Listado de medicamentos                       |
| POST   | `/requests`                   | Crea solicitud; valida campos si es NO POS    |
| GET    | `/requests?page=1&size=10`    | Solicitudes del usuario, paginadas            |

## Decisiones de diseño
- **Contraseñas**: se guardan con *hash* bcrypt + sal (irreversible), nunca en texto plano.
- **Microservicios**: cada API es un proceso independiente. Comparten la BD, pero `solicitudes_api` no consulta la tabla `users`: confía en el `sub` del JWT firmado.
- **Regla NO POS**: se valida en el frontend (UX) **y** en el backend (seguridad), porque el frontend se puede saltar.
- **Paginación** en servidor con `OFFSET/LIMIT`; la respuesta incluye `total` y `pages`.
