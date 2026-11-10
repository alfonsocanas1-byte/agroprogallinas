import streamlit as __st
from datetime import date
from supabase import create_client, Client

# Configuración de la página
__st.set_page_config(
    page_title="AgroPro Gallinas",
    page_icon="🥚",
    layout="wide"
)

# --- ESTILOS CSS PERSONALIZADOS PARA LA BARRA LATERAL ---
__st.markdown("""
<style>
    /* Estilo para los elementos privados en la barra lateral */
    section[data-testid="stSidebar"] div.row-widget.stRadio div[role="radiogroup"] label span p:has-text("🔒") {
        color: #1E90FF !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

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

# Menú principal ordenado según tus indicaciones
menu = __st.sidebar.selectbox(
    "Menú Principal",
    [
        "📊 Resumen General", 
        "📦 Producción Diaria", 
        "🌽 Gestión Comida Gallinas", 
        "📋 Historial y Lotes",
        "🔒 Huevos Venta Ana Lu", 
        "🔒 Fincas sostenibles: Las Palmas"
    ]
)

# ==========================================
# 1. RESUMEN GENERAL (PANTALLA PRINCIPAL)
# ==========================================
if menu == "📊 Resumen General":
    __st.header("Huevos y Bultos de Comida desde 7 Noviembre 2026")
    
    col1, col2, col3 = __st.columns(3)
    
    try:
        prod_res = supabase.table("huevosrecogidos").select("*").execute()
        data_rows = prod_res.data if prod_res and prod_res.data else []
        total_huevos = sum([row.get("huevos recolectados", 0) for row in data_rows]) if data_rows else 0
        total_rotos = sum([row.get("huevos rotos", 0) for row in data_rows]) if data_rows else 0
        
        comida_res = supabase.table("comprabultoscomida").select("*").execute()
        data_comida = comida_res.data if comida_res and comida_res.data else []
        total_bultos = len(data_comida) if data_comida else 0
        
        col1.metric("Total Huevos Recolectados", f"{total_huevos:,}")
        col2.metric("Total Huevos Rotos", f"{total_rotos:,}")
        col3.metric("Registros de Bultos Comprados", f"{total_bultos:,}")
            
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
    __st.write("Registra la compra de bultos de concentrado para las gallinas con su respectivo peso, marca y comentarios.")
    
    with __st.form("form_comida"):
        fecha_compra_bulto = __st.date_input("Fecha Compra Bulto", value=date.today())
        
        col_C1, col_C2 = __st.columns(2)
        with col_C1:
            kg_en_este_bulto = __st.number_input("Kg en este bulto", min_value=1, step=1, value=40)
        with col_C2:
            marca_bulto = __st.text_input("Marca Bulto")
            
        motivo_comentarios = __st.text_area("Motivo / Comentarios (Opcional)")
            
        submitted_comida = __st.form_submit_button("Guardar Compra de Comida")
        
        if submitted_comida:
            try:
                data_comida = {
                    "fecha compra bulto": str(fecha_compra_bulto),
                    "kg en este bulto": int(kg_en_este_bulto),
                    "marca bulto": str(marca_bulto),
                    "motivo/comentarios": str(motivo_comentarios) if motivo_comentarios else None
                }
                supabase.table("comprabultoscomida").insert(data_comida).execute()
                
                __st.success("¡Compra de comida registrada con éxito en Supabase!")
                __st.markdown("### 📝 Resumen del Registro Guardado:")
                __st.info(
                    f"- **Fecha Compra:** {fecha_compra_bulto}\n"
                    f"- **Kg en este Bulto:** {kg_en_este_bulto} kg\n"
                    f"- **Marca Bulto:** {marca_bulto}\n"
                    f"- **Motivo/Comentarios:** {motivo_comentarios if motivo_comentarios else 'Ninguno'}"
                )
            except Exception as e:
                __st.error(f"Error al guardar en Supabase: {e}")

# ==========================================
# 4. HISTORIAL Y LOTES
# ==========================================
elif menu == "📋 Historial y Lotes":
    __st.header("Historial General de Operaciones")
    __st.write("Consulta detallada de todos los registros almacenados en Supabase.")
    
    __st.subheader("🥚 Historial de Huevos Recogidos")
    try:
        response = supabase.table("huevosrecogidos").select("*").execute()
        if response.data:
            __st.dataframe(response.data, use_container_width=True)
        else:
            __st.info("Aún no hay registros en la tabla `huevosrecogidos`.")
    except Exception as e:
        __st.warning(f"No se pudo cargar el historial de huevos: {e}")
        
    __st.markdown("---")
    __st.subheader("🌽 Historial de Compras de Comida (`comprabultoscomida`)")
    try:
        resp_comida = supabase.table("comprabultoscomida").select("*").execute()
        if resp_comida.data:
            __st.dataframe(resp_comida.data, use_container_width=True)
        else:
            __st.info("Aún no hay registros en la tabla `comprabultoscomida`.")
    except Exception as e:
        __st.warning(f"No se pudo cargar el historial de comida: {e}")

# ==========================================
# 5. HUEVOS VENTA ANA LU (PRIVADO)
# ==========================================
elif menu == "🔒 Huevos Venta Ana Lu":
    __st.markdown("<h1 style='color: #1E90FF;'>🔒 Módulo Privado: Huevos Venta Ana Lu</h1>", unsafe_allow_html=True)
    __st.write("Control exclusivo para ventas realizadas con nuestra aliada Ana Lu.")
    
    password_analu = __st.text_input("Ingrese la contraseña de acceso", type="password")
    
    if password_analu == "202020":
        __st.success("¡Acceso concedido al módulo de Ana Lu!")
        __st.markdown("---")
        
        __st.subheader("📦 Registro de Venta de Panales AA")
        
        with __st.form("form_huevos_analu"):
            fecha_venta = __st.date_input("Fecha Venta", value=date.today())
            
            col_u1, col_u2 = __st.columns(2)
            with col_u1:
                num_panales = __st.number_input("Número Panales AA Vendidos", min_value=1, step=1, value=1)
                precio_compra = __st.number_input("precio compra panal ($)", min_value=0.0, step=100.0, value=0.0)
            with col_u2:
                precio_venta = __st.number_input("precio venta panal ($)", min_value=0.0, step=100.0, value=0.0)
                
                ganancia_venta = (precio_venta - precio_compra) * num_panales
                __st.markdown(f"**Ganancia Total Calculada:**")
                __st.markdown(f"### ${ganancia_venta:,.2f}")
                
            submitted_analu = __st.form_submit_button("Guardar Venta Ana Lu")
            
            if submitted_analu:
                try:
                    data_analu = {
                        "fecha venta": str(fecha_venta),
                        "número panales AA vendidos": int(num_panales),
                        "precio compra panales AA": float(precio_compra),
                        "precio venta panales": float(precio_venta),
                        "ganancia venta": float(ganancia_venta)
                    }
                    supabase.table("huevosanalu").insert(data_analu).execute()
                    __st.success("¡Venta registrada con éxito en Supabase!")
                except Exception as e:
                    __st.error(f"Error al guardar en Supabase: {e}")
                    
        __st.markdown("---")
        __st.subheader("📋 Tabla de Registros: Huevos Ana Lu (`huevosanalu`)")
        try:
            resp_analu_local = supabase.table("huevosanalu").select("*").execute()
            if resp_analu_local.data:
                __st.dataframe(resp_analu_local.data, use_container_width=True)
            else:
                __st.info("Aún no hay registros en la tabla `huevosanalu`.")
        except Exception as e:
            __st.warning(f"No se pudo cargar la tabla de Ana Lu: {e}")
                
    elif password_analu:
        __st.error("Contraseña incorrecta. Verifique e intente nuevamente.")
    else:
        __st.warning("🔒 Ingrese la contraseña requerida para visualizar y operar este módulo.")

# ==========================================
# 6. FINCAS SOSTENIBLES: LAS PALMAS (PRIVADO)
# ==========================================
elif menu == "🔒 Fincas sostenibles: Las Palmas":
    __st.markdown("<h1 style='color: #1E90FF;'>🔒 Módulo Privado: Fincas sostenibles: Las Palmas</h1>", unsafe_allow_html=True)
    __st.write("Acceso restringido para el control de suministros y personal.")
    
    password = __st.text_input("Ingrese la contraseña de acceso", type="password")
    
    if password == "505050":
        __st.success("¡Acceso concedido al núcleo privado de Las Palmas!")
        __st.markdown("---")
        
        # --- 1. RECIBO DE AGUA ---
        __st.subheader("💧 Control y Seguimiento de Recibo de Agua")
        sig_num_recibo = 1
        try:
            res_agua_ult = supabase.table("reciboagua").select("*").order("id", desc=True).limit(1).execute()
            if res_agua_ult.data and len(res_agua_ult.data) > 0:
                sig_num_recibo = int(res_agua_ult.data[0].get("número de recibo (incremental)", 0)) + 1
        except Exception:
            pass

        with __st.form("form_recibo_agua"):
            fecha_agua = __st.date_input("Fecha Recibo Agua", value=date.today())
            col_wa1, col_wa2 = __st.columns(2)
            with col_wa1:
                m3_agua = __st.number_input("Consumo (m³)", min_value=0, step=1, value=0)
                num_recibo = __st.number_input("Número de Recibo (Incremental)", min_value=1, step=1, value=sig_num_recibo)
            with col_wa2:
                valor_agua = __st.number_input("Valor Recibo ($)", min_value=0.0, step=1000.0, value=0.0)
                __st.markdown(f"**Valor Registrado:**")
                __st.markdown(f"### ${valor_agua:,.2f}")
                
            submitted_agua = __st.form_submit_button("Guardar Recibo de Agua")
            if submitted_agua:
                try:
                    data_agua = {
                        "fecha recibo": str(fecha_agua),
                        "m3": int(m3_agua),
                        "valor recibo": float(valor_agua),
                        "estado": "no pagado",
                        "número de recibo (incremental)": int(num_recibo)
                    }
                    supabase.table("reciboagua").insert(data_agua).execute()
                    __st.success("¡Recibo de agua registrado con éxito!")
                    __st.rerun()
                except Exception as e:
                    __st.error(f"Error: {e}")
                    
        __st.markdown("---")
        __st.subheader("📋 Tabla y Gestión de Estados: Recibos de Agua (`reciboagua`)")
        try:
            resp_agua_local = supabase.table("reciboagua").select("*").order("id", desc=False).execute()
            if resp_agua_local.data:
                registros_agua = resp_agua_local.data
                __st.dataframe(registros_agua, use_container_width=True)
                
                __st.markdown("#### 🔄 Actualizar Estado de un Recibo")
                with __st.form("form_actualizar_estado_agua"):
                    opciones_recibos = {f"Recibo #{r.get('número de recibo (incremental)')} - Fecha: {r.get('fecha recibo')} (Actual: {r.get('estado')})": r['id'] for r in registros_agua}
                    recibo_seleccionado = __st.selectbox("Seleccione el recibo a modificar", list(opciones_recibos.keys()))
                    nuevo_estado = __st.selectbox("Nuevo Estado", ["no pagado", "pagado"])
                    
                    submitted_estado = __st.form_submit_button("Actualizar Estado en Supabase")
                    
                    if submitted_estado:
                        id_a_actualizar = opciones_recibos[recibo_seleccionado]
                        try:
                            supabase.table("reciboagua").update({"estado": nuevo_estado}).eq("id", id_a_actualizar).execute()
                            __st.success(f"¡Estado actualizado a '{nuevo_estado}' con éxito!")
                            __st.rerun()
                        except Exception as e:
                            __st.error(f"Error al actualizar estado: {e}")
            else:
                __st.info("Aún no hay registros en la tabla `reciboagua`.")
        except Exception as e:
            __st.warning(f"No se pudo cargar la tabla de recibo de agua: {e}")
                    
        __st.markdown("---")
        __st.markdown("---") # LÍNEA CLARA DE DIVISIÓN
        
        # --- 2. RECIBO DE LUZ ---
        __st.subheader("⚡ Control y Seguimiento de Recibo de Luz")
        with __st.form("form_recibo_luz"):
            fecha_luz = __st.date_input("Fecha de Recogida Recibo Luz", value=date.today())
            col_l1, col_l2 = __st.columns(2)
            with col_l1:
                consumo_kwh = __st.number_input("Consumo (kWh)", min_value=0, step=1, value=0)
            with col_l2:
                valor_luz = __st.number_input("Valor ($)", min_value=0, step=1000, value=0)
                __st.markdown(f"**Valor Registrado:**")
                __st.markdown(f"### ${valor_luz:,.2f}")  submitted_luz = __st.form_submit_button("Guardar Recibo de Luz")  if submitted_luz: try: data_luz = { "fecha de recogida recibo luz": str(fecha_luz), "consumo kwh": int(consumo_kwh), "valor $$$": int(valor_luz)
                    }
                    supabase.table("reciboluz").insert(data_luz).execute()
                    __st.success("¡Recibo de luz registrado con éxito!")
                    __st.rerun()
                except Exception as e:
                    __st.error(f"Error: {e}")
                    
        __st.markdown("---")
        __st.subheader("📋 Tabla de Recibo de Luz (`reciboluz`)")
        try:
            resp_luz_local = supabase.table("reciboluz").select("*").execute()
            if resp_luz_local.data:
                __st.dataframe(resp_luz_local.data, use_container_width=True)
            else:
                __st.info("Aún no hay registros en la tabla `reciboluz`.")
        except Exception as e:
            __st.warning(f"No se pudo cargar la tabla: {e}")
                
        __st.markdown("---")
        __st.markdown("---") # LÍNEA CLARA DE DIVISIÓN
        
        # --- 3. COMBUSTIBLE FIAT PULSE ---
        __st.subheader("⛽ Control de Combustible: FIAT PULSE Impetus Azul")
        km_ant_default = 0
        try:
            res_ult = supabase.table("combustiblefiat").select("*").order("id", desc=True).limit(1).execute()
            if res_ult.data and len(res_ult.data) > 0:
                km_ant_default = int(res_ult.data[0].get("kilometraje actual", 0))
        except Exception:
            pass

        with __st.form("form_combustible_fiat"):
            fecha_tanqueo = __st.date_input("Fecha de Tanqueo", value=date.today())
            estacion_servicio = __st.text_input("Estación de Servicio")
            col_f1, col_f2 = __st.columns(2)
            with col_f1:
                galones_actual = __st.number_input("Galones Actual (Tanqueados)", min_value=1, step=1, value=1)
                kilometraje_anterior = __st.number_input("Kilometraje Anterior", min_value=0, step=1, value=km_ant_default)
            with col_f2:
                kilometraje_actual = __st.number_input("Kilometraje Actual", min_value=km_ant_default, step=1, value=km_ant_default + 300)
                km_recorridos = kilometraje_actual - kilometraje_anterior
                km_galon_actual = (km_recorridos / galones_actual) if galones_actual > 0 else 0.0
                __st.markdown(f"**Km Recorridos:** {km_recorridos:,} km")
                __st.markdown(f"**Rendimiento:** {km_galon_actual:,.2f} km/gal")
                
            submitted_combustible = __st.form_submit_button("Guardar Registro de Combustible")
            if submitted_combustible:
                try:
                    data_combustible = {
                        "fecha tanqueo": str(fecha_tanqueo),
                        "estación servicio": str(estacion_servicio),
                        "galones actual": int(galones_actual),
                        "kilometraje anterior": int(kilometraje_anterior),
                        "kilometraje actual": int(kilometraje_actual),
                        "km/galón actual": float(km_galon_actual)
                    }
                    supabase.table("combustiblefiat").insert(data_combustible).execute()
                    __st.success("¡Tanqueo registrado con éxito!")
                    __st.rerun()
                except Exception as e:
                    __st.error(f"Error: {e}")
                    
        __st.markdown("---")
        __st.subheader("📋 Tabla de Combustible FIAT Pulse (`combustiblefiat`)")
        try:
            resp_combustible_local = supabase.table("combustiblefiat").select("*").execute()
            if resp_combustible_local.data:
                __st.dataframe(resp_combustible_local.data, use_container_width=True)
            else:
                __st.info("Aún no hay registros.")
        except Exception as e:
            __st.warning(f"No se pudo cargar la tabla: {e}")
                
        __st.markdown("---")
        __st.markdown("---") # LÍNEA CLARA DE DIVISIÓN
        
        # --- 4. PIPAS DE GAS ---
        __st.subheader("🔥 Control y Compra de Pipas de Gas")
        tipo_gas = __st.selectbox("Tipo de Presentación de Gas", ["Pipa Pequeña (Reserva)", "Pipa Mediana (Calentador de Agua)",