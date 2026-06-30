# Verdusoft-Backend

API REST para el sistema de gestion de inventario, compras y ventas.

## Stack

- **FastAPI** (Python 3.13)
- **Supabase** (PostgreSQL via PostgREST)
- **PyJWT** para validacion de tokens
- **slowapi** para rate limiting

## Requisitos

- Python 3.13+
- Entorno virtual (`.venv/`)

## Instalacion

```bash
cd Verdusoft-Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Variables de Entorno

Copiar `.env.example` a `.env` y completar:

```bash
cp .env.example .env
```

| Variable | Descripcion | Ejemplo |
|----------|-------------|---------|
| `SUPABASE_URL` | URL de tu proyecto Supabase | `https://abc123.supabase.co` |
| `SUPABASE_KEY` | Service Role Key (secreta) | `eyJhbGciOiJIUzI1NiIs...` |
| `SUPABASE_JWT_SECRET` | JWT Secret del proyecto | `ddZbwS+91/nvA9j6q54...` |
| `ADMIN_MASTER_KEY` | Clave maestra para registro de admin | `verdusoft-admin-2026` |

> **IMPORTANTE**: El `SUPABASE_KEY` debe ser la **Service Role Key** (no el `anon key`).
> El `SUPABASE_JWT_SECRET` se encuentra en: Supabase Dashboard > Project Settings > API > JWT Settings > JWT Secret.

## Como correr

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

La API estara disponible en `http://localhost:8000`.

## Autenticacion

El sistema usa **Supabase Auth** con JWT.

### Roles

- `admin`: Acceso completo a todos los endpoints.
- `public`: Solo acceso al catalogo de productos (`GET /api/productos/catalogo`).

### Flujo de Autenticacion

1. **Registro (primera vez)**:
   ```bash
   POST /api/auth/register
   Body: { "email": "admin@ejemplo.com", "password": "123456", "master_key": "verdusoft-admin-2026" }
   ```
   Requiere la `ADMIN_MASTER_KEY`. Crea el usuario en Supabase Auth con `role: admin`.

2. **Login**:
   El frontend usa `@supabase/supabase-js` para hacer `signInWithPassword(email, password)` directamente contra Supabase Auth.

3. **Uso de la API**:
   Enviar el token JWT en el header de cada request:
   ```
   Authorization: Bearer <token>
   ```

### Endpoints Publicos

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET | `/` | Bienvenida |
| GET | `/health` | Health check |
| POST | `/api/auth/register` | Registro de admin (requiere master key) |
| GET | `/api/productos/catalogo` | Catalogo publico de productos |

### Endpoints Protegidos (requieren Admin)

Todos los demas endpoints bajo `/api/*` requieren autenticacion con rol `admin`.

## Seguridad

- **CORS**: Configurado para permitir solo origenes especificos (`localhost:8080` y produccion).
- **Rate Limiting**: 100 requests/min por IP (global).
- **JWT Validation**: Los tokens se validan localmente con PyJWT usando el `SUPABASE_JWT_SECRET`.

## Arquitectura

```
Router -> Auth (JWT validation) -> Service -> Supabase Client (PostgREST)
```

### Transacciones Atomicas

Las operaciones criticas (crear/cancelar compras y ventas) se realizan via **Stored Procedures** en PostgreSQL para garantizar atomicidad:

- `crear_venta()`
- `crear_compra()`
- `cancelar_venta()`
- `cancelar_compra()`

Ver `supabase_functions.sql` para el codigo SQL.
