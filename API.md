# Verdusoft API - Documentacion de Endpoints

> Base URL: `/api`

---

## Categorias

| Metodo | Ruta | Descripcion | Acceso |
|--------|------|-------------|--------|
| GET | `/api/categorias` | Listar categorias (paginado, filtro `activo`) | Admin |
| GET | `/api/categorias/{id}` | Obtener categoria por ID | Admin |
| POST | `/api/categorias` | Crear categoria | Admin |
| PATCH | `/api/categorias/{id}` | Actualizar categoria | Admin |
| DELETE | `/api/categorias/{id}` | Desactivar categoria (soft-delete) | Admin |

---

## Proveedores

| Metodo | Ruta | Descripcion | Acceso |
|--------|------|-------------|--------|
| GET | `/api/proveedores` | Listar proveedores (paginado, filtro `activo`) | Admin |
| GET | `/api/proveedores/{id}` | Obtener proveedor por ID | Admin |
| POST | `/api/proveedores` | Crear proveedor | Admin |
| PATCH | `/api/proveedores/{id}` | Actualizar proveedor | Admin |
| DELETE | `/api/proveedores/{id}` | Desactivar proveedor (soft-delete) | Admin |

---

## Clientes

| Metodo | Ruta | Descripcion | Acceso |
|--------|------|-------------|--------|
| GET | `/api/clientes` | Listar clientes (paginado, filtro `activo`) | Admin |
| GET | `/api/clientes/{id}` | Obtener cliente por ID | Admin |
| POST | `/api/clientes` | Crear cliente | Admin |
| PATCH | `/api/clientes/{id}` | Actualizar cliente | Admin |
| DELETE | `/api/clientes/{id}` | Desactivar cliente (soft-delete) | Admin |

---

## Productos

| Metodo | Ruta | Descripcion | Acceso |
|--------|------|-------------|--------|
| GET | `/api/productos` | Listar productos con filtros (nombre, categoria, codigo, activo, stock_bajo) | Admin |
| GET | `/api/productos/catalogo` | Listado publico: solo `id_producto`, `nombre`, `precio_actual` | **Publico** |
| GET | `/api/productos/stock-bajo` | Reporte de productos con stock bajo | Admin |
| GET | `/api/productos/{id}` | Obtener producto por ID (incluye categoria) | Admin |
| POST | `/api/productos` | Crear producto | Admin |
| PATCH | `/api/productos/{id}` | Actualizar producto | Admin |
| DELETE | `/api/productos/{id}` | Desactivar producto (soft-delete) | Admin |

---

## Compras

| Metodo | Ruta | Descripcion | Acceso |
|--------|------|-------------|--------|
| GET | `/api/compras` | Listar compras con filtros (fecha, proveedor, estado) | Admin |
| GET | `/api/compras/{id}` | Obtener compra por ID con detalles y proveedor | Admin |
| POST | `/api/compras` | Crear compra con detalles (suma stock + calcula total) | Admin |
| PATCH | `/api/compras/{id}` | Actualizar encabezado de compra | Admin |
| DELETE | `/api/compras/{id}` | Cancelar compra (revierte stock) | Admin |

---

## Ventas

| Metodo | Ruta | Descripcion | Acceso |
|--------|------|-------------|--------|
| GET | `/api/ventas` | Listar ventas con filtros (fecha, cliente, metodo_pago, estado) | Admin |
| GET | `/api/ventas/{id}` | Obtener venta por ID con detalles y cliente | Admin |
| POST | `/api/ventas` | Crear venta con detalles (descuenta stock + calcula total) | Admin |
| PATCH | `/api/ventas/{id}` | Actualizar encabezado de venta | Admin |
| DELETE | `/api/ventas/{id}` | Cancelar venta (revierte stock) | Admin |

---

## Otros

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/` | Mensaje de bienvenida de la API |
| GET | `/health` | Health check (verifica conexion con Supabase) |
| GET | `/docs` | Swagger UI (documentacion interactiva) |
| GET | `/redoc` | ReDoc (documentacion alternativa) |

---

## Total de Endpoints: **34**

---

## Notas Tecnicas

- **Transacciones atomicas**: Compras y ventas usan stored procedures de PostgreSQL. Si falla un paso, se hace ROLLBACK completo.
- **Movimiento de stock**: Las compras suman stock, las ventas restan stock. Cancelar una operacion revierte el movimiento.
- **Calculo de totales**: Subtotal y total se calculan en el backend. El frontend no necesita enviarlos.
- **Soft-delete**: Las entidades maestras (categorias, proveedores, clientes, productos) usan soft-delete cambiando `activo = false`.
