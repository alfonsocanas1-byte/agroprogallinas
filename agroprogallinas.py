import streamlit as __st
from datetime import date
from supabase import create_client, Client

# Configuración de la página
__st.set_page_config(
    page_title="AgroPro Gallinas",
    page_icon="🥚",
    layout="wide"
)

# Inicializar conexión con Supabase desde los secretos de Streamlit (.streamlit/secrets.toml)
@__st.cache_resource
def init_supabase() -> Client:
    url = __st.secrets["supabase"]["url"]
    key = __st.secrets["supabase"]["key"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    __st.error(f"Error conectando a Supabase. Verifica tus secretos. Detalles: {e}")
    __st.stop()

# --- TÍTULO Y MENÚ PRINCIPAL ---
__st.title("🥚 AgroPro Gallinas")
__st.markdown("---")

menu = __st.sidebar.selectbox(
    "Menú Principal",
    ["📊 Resumen General", "📦 Producción Diaria", "💰 Ventas y Clientes", "📋 Inventario y Lotes"]
)

# ==========================================
# 1. RESUMEN GENERAL
# ==========================================
if menu == "📊 Resumen General":
    __st.header("Panel de Control Diario")
    
    col1, col2, col3 = __st.columns(3)
    
    try:
        prod_res = supabase.table("huevosrecogidos").select("huevos recolectados, huevos rotos").execute()
        ventas_res = supabase.table("ventas_huevos").select("total_venta, cantidad_vendida").execute()
        
        total_huevos = sum([row["huevos recolectados"] for row in prod_res.data]) if prod_res.data else 0
        total_rotos = sum([row["huevos rotos"] for row in prod_res.data]) if prod_res.data else 0
        total_ventas_dinero = sum([row["total_venta"] for row in ventas_res.data]) if ventas_res.data else 0
        
        col1.metric("Huevos Producidos", f"{total_huevos:,}")
        col2.metric("Huevos Rotos / Dañados", f"{total_rotos:,}")
        col3.metric("Ingresos Totales", f"${total_ventas_dinero:,.2f}")
        
    except Exception as e:
        __st.info("Configura tus tablas en Supabase para visualizar las métricas en tiempo real.")

    __st.markdown("### Estado del Universo Productivo")
    __st.write("Bienvenido al núcleo de control. Selecciona una sección en el panel lateral para registrar la producción o gestionar las ventas.")

# ==========================================
# 2. PRODUCCIÓN DIARIA
# ==========================================
elif menu == "📦 Producción Diaria":
    __st.header("Registro de Producción Diaria")
    __st.write("Registra la recolección diaria de los galpones.")
    
    with __st.form("form_produccion"):
        fecha_prod = __st.date_input("Fecha de Registro", value=date.today())
        lote_galpon = __st.number_input("Identificador de Lote", min_value=1, step=1, value=1)
        
        col_A, col_B = __st.columns(2)
        with col_A:
            cant_huevos = __st.number_input("Huevos Recolectados (Unidades)", min_value=0, step=1)
        with col_B:
            cant_rotos = __st.number_input("Huevos Rotos o Manchados", min_value=0, step=1)
            
        submitted = __st.form_submit_button("Guardar Producción")
        
        if submitted:
            try:
                data = {
                    "fecha registro": str(fecha_prod),
                    "identificador lote": int(lote_galpon),
                    "huevos recolectados": int(cant_huevos),
                    "huevos rotos": int(cant_rotos)
                }
                supabase.table("huevosrecogidos").insert(data).execute()
                
                # Confirmación detallada abajo del formulario
                __st.success("¡Producción registrada con éxito en la base de datos!")
                __st.markdown("### 📝 Resumen del Registro Guardado:")
                __st.info(
                    f"- **Fecha:** {fecha_prod}\n"
                    f"- **Identificador de Lote:** {lote_galpon}\n"
                    f"- **Huevos Recolectados:** {cant_huevos:,} unidades\n"
                    f"- **Huevos Rotos:** {cant_rotos:,} unidades"
                )
            except Exception as e:
                __st.error(f"Error al guardar en Supabase: {e}")

# ==========================================
# 3. VENTAS Y CLIENTES
# ==========================================
elif menu == "💰 Ventas y Clientes":
    __st.header("Control de Ventas")
    
    with __st.form("form_ventas"):
        fecha_venta = __st.date_input("Fecha de Venta", value=date.today())
        cliente = __st.text_input("Nombre del Cliente / Comprador")
        col_V1, col_V2 = __st.columns(2)
        with col_V1:
            cant_vendida = __st.number_input("Cantidad Vendida (Huevos)", min_value=0, step=1)
        with col_V2:
            total_venta = __st.number_input("Valor Total de la Venta ($)", min_value=0.0, step=100.0)
            
        submitted_venta = __st.form_submit_button("Registrar Venta")
        
        if submitted_venta:
            try:
                data_venta = {
                    "fecha": str(fecha_venta),
                    "cliente": cliente,
                    "cantidad_vendida": cant_vendida,
                    "total_venta": total_venta
                }
                supabase.table("ventas_huevos").insert(data_venta).execute()
                __st.success("¡Venta registrada exitosamente!")
            except Exception as e:
                __st.error(f"Error al registrar la venta: {e}")

# ==========================================
# 4. INVENTARIO Y LOTES
# ==========================================
elif menu == "📋 Inventario y Lotes":
    __st.header("Gestión de Lotes y Estado Actual")
    __st.write("Consulta el historial completo de los registros sincronizados en Supabase.")
    
    try:
        response = supabase.table("huevosrecogidos").select("*").execute()
        if response.data:
            __st.subheader("📋 Historial de Huevos Recogidos")
            __st.dataframe(response.data, use_container_width=True)
        else:
            __st.info("Aún no hay registros de producción almacenados en la tabla `huevosrecogidos`.")
    except Exception as e:
        __st.warning(f"No se pudo cargar el historial: {e}")