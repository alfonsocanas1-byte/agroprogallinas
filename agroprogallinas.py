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
    [
        "📊 Resumen General", 
        "📦 Producción Diaria", 
        "🌽 Gestión Comida Gallinas", 
        "🔒 Fincas sostenibles: Las Palmas", 
        "📋 Historial y Lotes"
    ]
)

# ==========================================
# 1. RESUMEN GENERAL (PANTALLA PRINCIPAL)
# ==========================================
if menu == "📊 Resumen General":
    __st.header("Huevos y Bultos de Comida desde 7 Noviembre 2026")
    
    col1, col2, col3 = __st.columns(3)
    
    try:
        # 1. Consultar huevos
        prod_res = supabase.table("huevosrecogidos").select("*").execute()
        data_rows = prod_res.data if prod_res and prod_res.data else []
        total_huevos = sum([row.get("huevos recolectados", 0) for row in data_rows]) if data_rows else 0
        total_rotos = sum([row.get("huevos rotos", 0) for row in data_rows]) if data_rows else 0
        
        # 2. Consultar bultos de comida
        comida_res = supabase.table("comprabultoscomida").select("*").execute()
        data_comida = comida_res.data if comida_res and comida_res.data else []
        total_bultos = sum([row.get("cantidad bultos 50 kg concentrado", 0) for row in data_comida]) if data_comida else 0
        
        col1.metric("Total Huevos Recolectados", f"{total_huevos:,}")
        col2.metric("Total Huevos Rotos", f"{total_rotos:,}")
        col3.metric("Bultos 50 kg Comprados", f"{total_bultos:,}")
            
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
            marca_bultos = __st.text_input("Marca de los Bultos (Texto)")
            
        submitted_comida = __st.form_submit_button("Guardar Compra de Comida")
        
        if submitted_comida:
            try:
                data_comida = {
                    "fecha compra": str(fecha_compra),
                    "cantidad bultos 50 kg concentrado": int(cantidad_bultos),
                    "marca bultos": str(marca_bultos)
                }
                supabase.table("comprabultoscomida").insert(data_comida).execute()
                
                __st.success("¡Compra de comida registrada con éxito en Supabase!")
                __st.markdown("### 📝 Resumen del Registro Guardado:")
                __st.info(
                    f"- **Fecha Compra:** {fecha_compra}\n"
                    f"- **Cantidad Bultos (50 kg):** {cantidad_bultos}\n"
                    f"- **Marca de los Bultos:** {marca_bultos}"
                )
            except Exception as e:
                __st.error(f"Error al guardar en Supabase: {e}")

# ==========================================
# 4. FINCAS SOSTENIBLES: LAS PALMAS (PRIVADO)
# ==========================================
elif menu == "🔒 Fincas sostenibles: Las Palmas":
    __st.header("🔒 Módulo Privado: Fincas sostenibles: Las Palmas")
    __st.write("Acceso restringido para el control de suministros y personal.")
    
    password = __st.text_input("Ingrese la contraseña de acceso", type="password")
    
    if password == "505050":
        __st.success("¡Acceso concedido al núcleo privado de Las Palmas!")
        __st.markdown("---")
        
        # 1. Compras de pipas de gas
        __st.subheader("🔥 Control y Compra de Pipas de Gas")
        
        tipo_gas = __st.selectbox(
            "Tipo de Presentación de Gas",
            [
                "Pipa Pequeña (Reserva)", 
                "Pipa Mediana (Calentador de Agua)", 
                "Pipa Grande (Cocina)", 
                "Pipa Grande (Jacuzzi)"
            ]
        )
        
        with __st.form("form_gas_palmas"):
            fecha_gas = __st.date_input("Fecha de Compra General", value=date.today())
            
            col_g1, col_g2 = __st.columns(2)
            with col_g1:
                cant_gas = __st.number_input("Cantidad", min_value=1, step=1, value=1)
                precio_presentacion = __st.number_input("Precio por Presentación ($)", min_value=0.0, step=100.0)
            with col_g2:
                precio_total = cant_gas * precio_presentacion
                __st.markdown(f"**Precio Total Calculado:**")
                __st.markdown(f"### ${precio_total:,.2f}")
                
            submitted_gas = __st.form_submit_button("Guardar Compra de Gas")
            
            if submitted_gas:
                try:
                    data_gas = {
                        "fecha de compra general": str(fecha_gas),
                        "tipo de presentación gas": str(tipo_gas),
                        "cantidad por tipo de presentación gas": int(cant_gas),
                        "precio por presentación": float(precio_presentacion),
                        "precio total compra": float(precio_total)
                    }
                    supabase.table("consumogas").insert(data_gas).execute()
                    
                    __st.success("¡Compra de gas registrada con éxito en Supabase!")
                    __st.markdown("### 📝 Resumen del Gas Registrado:")
                    __st.info(
                        f"- **Fecha:** {fecha_gas}\n"
                        f"- **Presentación:** {tipo_gas}\n"
                        f"- **Cantidad:** {cant_gas}\n"
                        f"- **Precio Unitario:** ${precio_presentacion:,.2f}\n"
                        f"- **Precio Total:** ${precio_total:,.2f}"
                    )
                except Exception as e:
                    __st.error(f"Error al guardar en Supabase: {e}")
                    
        # Tabla de Supabase de Consumo de Gas debajo de sus campos
        __st.markdown("---")
        __st.subheader("📋 Tabla de Consumo y Compras de Gas (`consumogas`)")
        try:
            resp_gas_local = supabase.table("consumogas").select("*").execute()
            if resp_gas_local.data:
                __st.dataframe(resp_gas_local.data, use_container_width=True)
            else:
                __st.info("Aún no hay registros en la tabla `consumogas`.")
        except Exception as e:
            __st.warning(f"No se pudo cargar la tabla de gas: {e}")
                
        __st.markdown("---")
        
        # 2. Gestión de Alimento para Perros
        __st.subheader("🐶 Gestión de Alimento para Perros")
        with __st.form("form_bultoperros"):
            fecha_compra_perros = __st.date_input("Fecha Compra", value=date.today())
            marca_perros = __st.text_input("Marca del Alimento")
            
            col_p1, col_p2 = __st.columns(2)
            with col_p1:
                kg_bulto = __st.number_input("Kg el Bulto", min_value=1, step=1, value=20)
                num_bultos = __st.number_input("Número de Bultos", min_value=1, step=1, value=1)
            with col_p2:
                precio_unitario = __st.number_input("Precio Unitario ($)", min_value=0.0, step=100.0, value=0.0)
                precio_total_compra = num_bultos * precio_unitario
                __st.markdown(f"**Precio Total Calculado:**")
                __st.markdown(f"### ${precio_total_compra:,.2f}")
                
            submitted_perros = __st.form_submit_button("Guardar Compra Alimento Perros")
            
            if submitted_perros:
                try:
                    data_perros = {
                        "fecha compra": str(fecha_compra_perros),
                        "marca": str(marca_perros),
                        "kg el bulto": int(kg_bulto),
                        "número de bultos": int(num_bultos),
                        "precio unitario": float(precio_unitario),
                        "precio total compra": float(precio_total_compra)
                    }
                    supabase.table("bultoperros").insert(data_perros).execute()
                    
                    __st.success("¡Compra de alimento para perros registrada con éxito en Supabase!")
                    __st.markdown("### 📝 Resumen del Registro Guardado:")
                    __st.info(
                        f"- **Fecha Compra:** {fecha_compra_perros}\n"
                        f"- **Marca:** {marca_perros}\n"
                        f"- **Kg por Bulto:** {kg_bulto} kg\n"
                        f"- **Número de Bultos:** {num_bultos}\n"
                        f"- **Precio Unitario:** ${precio_unitario:,.2f}\n"
                        f"- **Precio Total:** ${precio_total_compra:,.2f}"
                    )
                except Exception as e:
                    __st.error(f"Error al guardar en Supabase: {e}")
                    
        # Tabla de Supabase de Alimento para Perros debajo de sus campos
        __st.markdown("---")
        __st.subheader("📋 Tabla de Alimento para Perros (`bultoperros`)")
        try:
            resp_perros_local = supabase.table("bultoperros").select("*").execute()
            if resp_perros_local.data:
                __st.dataframe(resp_perros_local.data, use_container_width=True)
            else:
                __st.info("Aún no hay registros en la tabla `bultoperros`.")
        except Exception as e:
            __st.warning(f"No se pudo cargar la tabla de perros: {e}")
                
        __st.markdown("---")
        
        # 3. Gestión de personal / Asistencia de Milena
        __st.subheader("👥 Gestión de Personal: Asistencia de Milena")
        with __st.form("form_milena_palmas"):
            fecha_asist = __st.date_input("Fecha de Asistencia", value=date.today())
            pago_dia = __st.number_input("Pago del Día ($)", min_value=0.0, step=1000.0, value=0.0)
            
            submitted_milena = __st.form_submit_button("Guardar Asistencia de Milena")
            
            if submitted_milena:
                try:
                    data_milena = {
                        "fecha de asistencia": str(fecha_asist),
                        "pago del día": int(pago_dia)
                    }
                    supabase.table("asistenciamilena").insert(data_milena).execute()
                    
                    __st.success("¡Asistencia de Milena registrada con éxito en Supabase!")
                    __st.markdown("### 📝 Resumen de Asistencia:")
                    __st.info(
                        f"- **Fecha de Asistencia:** {fecha_asist}\n"
                        f"- **Pago del Día:** ${pago_dia:,.2f}"
                    )
                except Exception as e:
                    __st.error(f"Error al guardar en Supabase: {e}")
                    
        # Tabla de Supabase de Asistencia de Milena debajo del formulario
        __st.markdown("---")
        __st.subheader("📋 Tabla de Asistencia de Milena (`asistenciamilena`)")
        try:
            resp_milena_local = supabase.table("asistenciamilena").select("*").execute()
            if resp_milena_local.data:
                __st.dataframe(resp_milena_local.data, use_container_width=True)
            else:
                __st.info("Aún no hay registros en la tabla `asistenciamilena`.")
        except Exception as e:
            __st.warning(f"No se pudo cargar la tabla de asistencia: {e}")
                
    elif password:
        __st.error("Contraseña incorrecta. Verifique e intente nuevamente.")
    else:
        __st.warning("🔒 Ingrese la contraseña requerida para visualizar y operar este módulo.")

# ==========================================
# 5. HISTORIAL Y LOTES
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