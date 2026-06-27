-- =============================================================================
-- Funciones PostgreSQL para transacciones atomicas en Verdusoft
-- Ejecutar TODO este archivo en el SQL Editor de Supabase
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. CREAR VENTA (atomica)
-- Inserta venta, detalles, calcula totales y descuenta stock.
-- Si falla en cualquier paso, hace ROLLBACK completo.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION crear_venta(
  p_numero_ticket text DEFAULT NULL,
  p_id_cliente integer DEFAULT NULL,
  p_fecha timestamptz DEFAULT now(),
  p_metodo_pago text DEFAULT 'efectivo',
  p_observaciones text DEFAULT NULL,
  p_estado text DEFAULT 'completada',
  p_detalles jsonb DEFAULT '[]'::jsonb
)
RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
  v_id_venta integer;
  v_total numeric := 0;
  det record;
  v_stock_actual integer;
BEGIN
  -- ---------------------------------------------------------------------------
  -- Paso 1: Validar stock y calcular total
  -- ---------------------------------------------------------------------------
  FOR det IN
    SELECT *
    FROM jsonb_to_recordset(p_detalles)
    AS x(id_producto integer, cantidad integer, precio_unitario numeric, descuento numeric)
  LOOP
    SELECT stock
    INTO v_stock_actual
    FROM producto
    WHERE id_producto = det.id_producto
    FOR UPDATE;  -- bloquea la fila hasta el COMMIT

    IF v_stock_actual IS NULL THEN
      RAISE EXCEPTION 'Producto % no encontrado', det.id_producto;
    END IF;

    IF v_stock_actual < det.cantidad THEN
      RAISE EXCEPTION
        'Stock insuficiente para producto %. Stock actual: %, requerido: %',
        det.id_producto, v_stock_actual, det.cantidad;
    END IF;

    v_total := v_total + (det.cantidad * det.precio_unitario - COALESCE(det.descuento, 0));
  END LOOP;

  -- ---------------------------------------------------------------------------
  -- Paso 2: Insertar encabezado de venta
  -- ---------------------------------------------------------------------------
  INSERT INTO venta (numero_ticket, id_cliente, fecha, metodo_pago, observaciones, estado, total)
  VALUES (p_numero_ticket, p_id_cliente, p_fecha, p_metodo_pago, p_observaciones, p_estado, v_total)
  RETURNING id_venta INTO v_id_venta;

  -- ---------------------------------------------------------------------------
  -- Paso 3: Insertar detalles y descontar stock
  -- ---------------------------------------------------------------------------
  FOR det IN
    SELECT *
    FROM jsonb_to_recordset(p_detalles)
    AS x(id_producto integer, cantidad integer, precio_unitario numeric, descuento numeric)
  LOOP
    INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, descuento, subtotal)
    VALUES (
      v_id_venta,
      det.id_producto,
      det.cantidad,
      det.precio_unitario,
      COALESCE(det.descuento, 0),
      det.cantidad * det.precio_unitario - COALESCE(det.descuento, 0)
    );

    UPDATE producto
    SET stock = stock - det.cantidad
    WHERE id_producto = det.id_producto;
  END LOOP;

  -- ---------------------------------------------------------------------------
  -- Resultado
  -- ---------------------------------------------------------------------------
  RETURN jsonb_build_object('id_venta', v_id_venta, 'total', v_total);
END;
$$;


-- -----------------------------------------------------------------------------
-- 2. CREAR COMPRA (atomica)
-- Inserta compra, detalles, calcula totales y suma stock.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION crear_compra(
  p_numero_factura text DEFAULT NULL,
  p_id_proveedor integer DEFAULT NULL,
  p_fecha timestamptz DEFAULT now(),
  p_observaciones text DEFAULT NULL,
  p_estado text DEFAULT 'completada',
  p_detalles jsonb DEFAULT '[]'::jsonb
)
RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
  v_id_compra integer;
  v_total numeric := 0;
  det record;
BEGIN
  -- ---------------------------------------------------------------------------
  -- Paso 1: Validar productos y calcular total
  -- ---------------------------------------------------------------------------
  FOR det IN
    SELECT *
    FROM jsonb_to_recordset(p_detalles)
    AS x(id_producto integer, cantidad integer, precio_unitario numeric)
  LOOP
    IF NOT EXISTS (SELECT 1 FROM producto WHERE id_producto = det.id_producto) THEN
      RAISE EXCEPTION 'Producto % no encontrado', det.id_producto;
    END IF;

    v_total := v_total + (det.cantidad * det.precio_unitario);
  END LOOP;

  -- ---------------------------------------------------------------------------
  -- Paso 2: Insertar encabezado de compra
  -- ---------------------------------------------------------------------------
  INSERT INTO compra (numero_factura, id_proveedor, fecha, observaciones, estado, total)
  VALUES (p_numero_factura, p_id_proveedor, p_fecha, p_observaciones, p_estado, v_total)
  RETURNING id_compra INTO v_id_compra;

  -- ---------------------------------------------------------------------------
  -- Paso 3: Insertar detalles y sumar stock
  -- ---------------------------------------------------------------------------
  FOR det IN
    SELECT *
    FROM jsonb_to_recordset(p_detalles)
    AS x(id_producto integer, cantidad integer, precio_unitario numeric)
  LOOP
    INSERT INTO detalle_compra (id_compra, id_producto, cantidad, precio_unitario, subtotal)
    VALUES (
      v_id_compra,
      det.id_producto,
      det.cantidad,
      det.precio_unitario,
      det.cantidad * det.precio_unitario
    );

    UPDATE producto
    SET stock = stock + det.cantidad
    WHERE id_producto = det.id_producto;
  END LOOP;

  RETURN jsonb_build_object('id_compra', v_id_compra, 'total', v_total);
END;
$$;


-- -----------------------------------------------------------------------------
-- 3. CANCELAR VENTA (atomica)
-- Cambia estado a 'cancelada' y revierte el stock descontado.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION cancelar_venta(p_id_venta integer)
RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
  det record;
  v_estado text;
BEGIN
  SELECT estado INTO v_estado FROM venta WHERE id_venta = p_id_venta;

  IF v_estado IS NULL THEN
    RAISE EXCEPTION 'Venta % no encontrada', p_id_venta;
  END IF;

  IF v_estado = 'cancelada' THEN
    RAISE EXCEPTION 'Venta % ya esta cancelada', p_id_venta;
  END IF;

  -- Revertir stock
  FOR det IN
    SELECT id_producto, cantidad
    FROM detalle_venta
    WHERE id_venta = p_id_venta
  LOOP
    UPDATE producto
    SET stock = stock + det.cantidad
    WHERE id_producto = det.id_producto;
  END LOOP;

  -- Actualizar estado
  UPDATE venta SET estado = 'cancelada' WHERE id_venta = p_id_venta;

  RETURN jsonb_build_object('mensaje', 'Venta cancelada exitosamente');
END;
$$;


-- -----------------------------------------------------------------------------
-- 4. CANCELAR COMPRA (atomica)
-- Cambia estado a 'cancelada' y revierte el stock sumado.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION cancelar_compra(p_id_compra integer)
RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
  det record;
  v_estado text;
BEGIN
  SELECT estado INTO v_estado FROM compra WHERE id_compra = p_id_compra;

  IF v_estado IS NULL THEN
    RAISE EXCEPTION 'Compra % no encontrada', p_id_compra;
  END IF;

  IF v_estado = 'cancelada' THEN
    RAISE EXCEPTION 'Compra % ya esta cancelada', p_id_compra;
  END IF;

  -- Revertir stock
  FOR det IN
    SELECT id_producto, cantidad
    FROM detalle_compra
    WHERE id_compra = p_id_compra
  LOOP
    UPDATE producto
    SET stock = stock - det.cantidad
    WHERE id_producto = det.id_producto;
  END LOOP;

  -- Actualizar estado
  UPDATE compra SET estado = 'cancelada' WHERE id_compra = p_id_compra;

  RETURN jsonb_build_object('mensaje', 'Compra cancelada exitosamente');
END;
$$;
