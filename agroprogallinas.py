import streamlit as __st
from datetime import date
from supabase import create_client, Client

# Configuración de la página
__st.set_page_config(
    page_title="AgroPro Gallinas",
    page_icon="🥚",
    layout="wide"
)

# Inicializar conexión con Supabase desde los secretos de Streamlit
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

# --- SALUDO Y TÍTULO PRINCIPAL ---
__st.subheader("¡Hola, Alfonso! Bienvenido al núcleo de control de AgroPro. 🦅🚀")
__st.title("🥚 AgroPro Gallinas")
__st.markdown("---")

menu = __st.sidebar.selectbox(
    "Menú Principal",
    ["📊 Resumen General", "📦 Producción Diaria", "🌽 Gestión Comida Gallinas", "📋 Historial y Lotes"]
)

# ==========================================
# 1. RESUMEN GENERAL (PANTALLA PRINCIPAL)
# ==========================================
if menu == "📊 Resumen General":
    __st.header("Huevos recolectados y rotos desde 7 Noviembre 2026")
    
    col1, col2 = __st.columns(2)
    
    try:
        # Consultamos todos los registros de la tabla huevosrecogidos
        prod_res = supabase.table("huevosrecogidos").select("*").execute()
        data_rows = prod_res.data if prod_res and prod_res.data else []
        
        total_huevos = sum([row.get("huevos recolectados", 0) for row in data_rows]) if data_rows else 0
        total_rotos = sum([row.get("huevos rotos", 0) for row in data_rows]) if data_rows else 0
        
        col1.metric("Total Huevos Recolectados", f"{total_huevos:,}")
        col2.metric("Total Huevos Rotos", f"{total_rotos:,}")
            
    except Exception as e:
        __st.error(f"No se pudieron cargar los datos de Supabase: {e}")

    __st.markdown("---")
    __st.markdown("### Estado del Universo Productivo")
    __st.write("Selecciona una sección en el panel lateral para registrar la producción diaria, administrar la comida o consultar el historial completo.")

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
# 3. GESTIÓN COMIDA GALLINAS
# ==========================================
elif menu == "🌽 Gestión Comida Gallinas":
    __st.header("Gestión de Compra y Bultos de Comida")
    __st.write("Registra la compra y suministro de bultos de concentrado para las gallinas.")
    
    with __st.form("form_comida"):
        fecha_compra = __st.date_input("Fecha de Compra", value=date.today())
        
        col_C1, col_C2 = __st.columns(2)
        with col_C1:
            cantidad_bultos = __st.number_input("Cantidad Bultos 50 kg Concentrado", min_value=0, step=1, value=1)
        with col_C2:
            marca_bultos = __st.number_input("Marca / Identificador de Bultos", min_value=1, step=1, value=1)
            
        submitted_comida = __st.form_submit_button("Guardar Compra de Comida")
        
        if submitted_comida:
            try:
                data_comida = {
                    "fecha compra": str(fecha_compra),
                    "cantidad bultos 50 kg concentrado": int(cantidad_bultos),
                    "marca bultos": int(marca_bultos)
                }
                supabase.table("comprabultoscomida").insert(data_comida).execute()
                
                __st.success("¡Compra de comida registrada con éxito en Supabase!")
                __st.markdown("### 📝 Resumen del Registro de Comida:")
                __st.info(
                    f"- **Fecha Compra:** {fecha_compra}\n"
                    f"- **Cantidad Bultos (50 kg):** {cantidad_bultos}\n"
                    f"- **Marca / ID de Bultos:** {marca_bultos}"
                )
            except Exception as e:
                __st.error(f"Error al guardar en Supabase: {e}")
                
    __st.markdown("---")
    __st.subheader("📋 Historial de Compras de Comida")
    try:
        resp_comida = supabase.table("comprabultoscomida").select("*").execute()
        if resp_comida.data:
            __st.dataframe(resp_comida.data, use_container_width=True)
        else:
            __st.info("Aún no hay registros en la tabla `comprabultoscomida`.")
    except Exception as e:
        __st.warning(f"No se pudo cargar el historial de comida: {e}")

# ==========================================
# 4. HISTORIAL Y LOTES
# ==========================================
elif menu == "📋 Historial y Lotes":
    __st.header("Historial de Huevos Recogidos")
    __st.write("Consulta detallada de todos los lotes y registros almacenados en Supabase.")
    
    try:
        response = supabase.table("huevosrecogidos").select("*").execute()
        if response.data:
            __st.dataframe(response.data, use_container_width=True)
        else:
            __st.info("Aún no hay registros de producción almacenados en la tabla `huevosrecogidos`.")
    except Exception as e:
        __st.warning(f"No se pudo cargar el historial: {e}")