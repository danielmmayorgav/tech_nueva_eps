# Solicitudes de Medicamentos — Prueba Técnica

Aplicación fullstack con **dos APIs independientes en Python (FastAPI)** y un **frontend en React (Vite)**, sobre **MySQL / MariaDB**.

| Componente        | Tecnología                         | Puerto |
|-------------------|------------------------------------|--------|
| `auth_api`        | FastAPI · SQLAlchemy · bcrypt · JWT | 8001   |
| `solicitudes_api` | FastAPI · SQLAlchemy · JWT          | 8002   |
| `frontend`        | React 18 · React Router · Axios     | 5173   |
| Base de datos     | MySQL (`tech_nueva_eps`)            | 3306   |

## Requisitos
- Python 3.12, Node.js 20+, MySQL 8 o MariaDB 10.5+.

## 1. Base de datos
```bash
mysql -u root -p --default-character-set=utf8mb4 < database/schema.sql
```
Crea las tablas `users`, `medications` y `requests`, y carga medicamentos de ejemplo (POS y NO POS).

## 2. APIs (repetir en `auth_api` y `solicitudes_api`)
```bash
cd auth_api
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env          # ajustar DATABASE_URL y SECRET_KEY
uvicorn main:app --reload --port 8001     # 8002 para solicitudes_api
```
> `SECRET_KEY` **debe ser igual** en ambas APIs: una firma el token y la otra lo verifica.

Documentación interactiva (Swagger): http://localhost:8001/docs y http://localhost:8002/docs

## 3. Frontend
```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```
Abrir http://localhost:5173

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
- **Teléfono como texto**: `requests.phone` pasó de `MEDIUMINT` a `varchar(20)` (un celular de 10 dígitos no cabe en MEDIUMINT y se perderían `+57` o ceros iniciales).
- **Paginación** en servidor con `OFFSET/LIMIT`; la respuesta incluye `total` y `pages`.
