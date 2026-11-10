
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="m13carclean - Sistema de Gestión", page_icon="🚗", layout="wide"
)

# Inicializar datos en la sesión si no existen
if "servicios" not in st.session_state:
    st.session_state.servicios = {
        "Auto - Básico": 15000,
        "Auto - Premium": 20000,
        "Camioneta - Básico": 25000,
        "Camioneta - Premium": 25000,  # Ajustado según tu indicación
        "SUV - Básico": 20000,
        "SUV - Premium": 25000,
        "Lavado Tapiz": 25000,
        "Servicio Detailing": 45000,
        "Lavado de Alfombra": 5000,
    }

if "registros" not in st.session_state:
    # DataFrame para ingresos y gastos
    st.session_state.registros = pd.DataFrame(
        columns=[
            "Fecha",
            "Tipo",
            "Cliente",
            "Patente",
            "Detalle",
            "Monto",
            "Metodo",
        ]
    )

if "clientes" not in st.session_state:
    st.session_state.clientes = pd.DataFrame(columns=["Nombre", "Patente"])

# Título Principal
st.title("🚗 m13carclean - Control de Gestión")
st.markdown("---")

# Menú lateral
menu = st.sidebar.selectbox(
    "Menú de Navegación",
    [
        "📊 Balance General",
        "➕ Registrar Ingreso / Gasto",
        "👥 Clientes y Vehículos",
        "⚙️ Configurar Servicios y Precios",
    ],
)

# ---------------------------------------------------------
# 1. BALANCE GENERAL
# ---------------------------------------------------------
if menu == "📊 Balance General":
  st.subheader("Resumen Financiero")

  df = st.session_state.registros

  if not df.empty:
    ingresos = df[df["Tipo"] == "Ingreso"]["Monto"].sum()
    gastos = df[df["Tipo"] == "Gasto"]["Monto"].sum()
    balance = ingresos - gastos

    col1, col2, col3 = st.columns(3)
    col1.metric("Ingresos Totales", f"${ingresos:,.0f}")
    col2.metric("Gastos Totales", f"${gastos:,.0f}")
    col3.metric(
        "Balance Actual",
        f"${balance:,.0f}",
        delta=f"${balance:,.0f}" if balance >= 0 else f"-${abs(balance):,.0f}",
    )

    st.markdown("---")
    st.subheader("Historial de Movimientos")
    st.dataframe(df, use_container_width=True)
  else:
    st.info(
        "Aún no hay registros financieros. Comienza agregando ingresos o"
        " gastos en la sección correspondiente."
    )

# ---------------------------------------------------------
# 2. REGISTRAR INGRESO / GASTO
# ---------------------------------------------------------
elif menu == "➕ Registrar Ingreso / Gasto":
  st.subheader("Registrar Movimiento")

  tipo_movimiento = st.radio(
      "¿Qué deseas registrar?", ["Ingreso (Lavado/Servicio)", "Gasto"]
  )

  with st.form("form_movimiento"):
    fecha = st.date_input("Fecha")

    if "Ingreso" in tipo_movimiento:
      cliente = st.text_input("Nombre del Cliente")
      patente = st.text_input("Patente del Vehículo").upper()

      # Seleccionar servicio de la lista configurable
      servicio_seleccionado = st.selectbox(
          "Tipo de Lavado / Servicio", list(st.session_state.servicios.keys())
      )
      monto = st.number_input(
          "Monto ($)",
          min_value=0,
          value=st.session_state.servicios[servicio_seleccionado],
          step=500,
      )
      detalle = servicio_seleccionado
    else:
      cliente = "N/A"
      patente = "N/A"
      detalle = st.text_input("Descripción del Gasto (ej. Insumos, Luz, Agua)")
      monto = st.number_input("Monto del Gasto ($)", min_value=0, step=500)

    metodo = st.selectbox(
        "Método de Pago / Salida", ["Efectivo", "Transferencia", "Tarjeta"]
    )

    submitted = st.form_submit_button("Guardar Registro")

    if submitted:
      nuevo_registro = pd.DataFrame(
          {
              "Fecha": [str(fecha)],
              "Tipo": ["Ingreso" if "Ingreso" in tipo_movimiento else "Gasto"],
              "Cliente": [cliente],
              "Patente": [patente],
              "Detalle": [detalle],
              "Monto": [monto],
              "Metodo": [metodo],
          }
      )

      st.session_state.registros = pd.concat(
          [st.session_state.registros, nuevo_registro], ignore_index=True
      )

      # Si es ingreso y tiene patente, guardarlo o actualizarlo en la base de clientes
      if "Ingreso" in tipo_movimiento and patente:
        nuevo_cliente = pd.DataFrame(
            {"Nombre": [cliente], "Patente": [patente]}
        )
        st.session_state.clientes = pd.concat(
            [st.session_state.clientes, nuevo_cliente], ignore_index=True
        ).drop_duplicates(subset=["Patente"])

      st.success("¡Movimiento registrado con éxito!")

# ---------------------------------------------------------
# 3. CLIENTES Y VEHÍCULOS
# ---------------------------------------------------------
elif menu == "👥 Clientes y Vehículos":
  st.subheader("Base de Clientes y Patentes Registradas")

  if not st.session_state.clientes.empty:
    st.dataframe(
        st.session_state.clientes,
        use_container_width=True,
        hide_index=True,
    )
  else:
    st.info(
        "Aún no hay clientes registrados. Se registrarán automáticamente al"
        " añadir un ingreso."
    )

# ---------------------------------------------------------
# 4. CONFIGURAR SERVICIOS Y PRECIOS
# ---------------------------------------------------------
elif menu == "⚙️ Configurar Servicios y Precios":
  st.subheader("Administrar Tipos de Lavado y Precios")
  st.markdown(
      "Aquí puedes modificar los precios actuales o agregar nuevos servicios"
      " según lo necesites."
  )

  # Formulario para modificar precios existentes
  with st.form("form_precios"):
    st.markdown("### Modificar Precios Actuales")
    nuevos_precios = {}
    for servicio, precio in st.session_state.servicios.items():
      nuevos_precios[servicio] = st.number_input(
          f"{servicio} ($)", value=precio, step=500, key=f"price_{servicio}"
      )

    actualizar = st.form_submit_button("Actualizar Precios")
    if actualizar:
      st.session_state.servicios = nuevos_precios
      st.success("¡Precios actualizados correctamente!")

  st.markdown("---")
  with st.form("form_nuevo_servicio"):
    st.markdown("### Agregar Nuevo Servicio")
    nuevo_nombre = st.text_input("Nombre del Nuevo Servicio/Lavado")
    nuevo_precio = st.number_input(
        "Precio Inicial ($)", min_value=0, step=500, value=10000
    )
    agregar = st.form_submit_button("Agregar Servicio")

    if agregar and nuevo_nombre:
      st.session_state.servicios[nuevo_nombre] = nuevo_precio
      st.success(f"¡Servicio '{nuevo_nombre}' agregado con éxito!")
      st.rerun()
