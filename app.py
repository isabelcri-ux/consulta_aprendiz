import streamlit as st
import pandas as pd
from io import BytesIO

# ── Configuración de página ──────────────────────────────────
st.set_page_config(
    page_title="Sistema Zajuna · SENA",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personalizado ────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #003820 0%, #00582E 100%);
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
[data-testid="stSidebar"] .stFileUploader label {
    color: #ffffff !important;
}

/* Métricas */
[data-testid="stMetric"] {
    background: #f8fafb;
    border-radius: 12px;
    padding: 16px 20px;
    border: 1px solid #e8edf0;
}
[data-testid="stMetricValue"] {
    font-weight: 700 !important;
    font-size: 2rem !important;
}

/* Tarjetas de aprendiz */
.aprendiz-card {
    background: white;
    border-radius: 12px;
    padding: 16px 20px;
    border: 1px solid #e8edf0;
    margin-bottom: 10px;
    transition: box-shadow .2s;
}
.aprendiz-card:hover {
    box-shadow: 0 4px 20px rgba(0,88,46,.10);
}

/* Badge de estado */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 12px;
    font-weight: 600;
}
.badge-ok    { background:#d4edda; color:#155724; }
.badge-pend  { background:#fff3cd; color:#856404; }
.badge-riesgo{ background:#f8d7da; color:#721c24; }
.badge-critico{background:#e2d9f3; color:#432874; }

/* Título principal */
.main-title {
    font-size: 2rem;
    font-weight: 700;
    color: #00582E;
    margin-bottom: 4px;
}
.main-sub {
    color: #6c757d;
    font-size: 1rem;
    margin-bottom: 24px;
}

/* Barra de progreso personalizada */
.prog-bar-wrap {
    background: #e9ecef;
    border-radius: 99px;
    height: 8px;
    width: 100%;
    overflow: hidden;
}
.prog-bar-fill {
    height: 8px;
    border-radius: 99px;
    background: linear-gradient(90deg, #00582E, #40c878);
}

/* Tabla de evidencias */
.ev-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid #f0f0f0;
    font-size: 13px;
}
.ev-row:last-child { border-bottom: none; }

/* Divider */
.sena-divider {
    border: none;
    border-top: 2px solid #00582E;
    margin: 24px 0 20px;
    opacity: .15;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# CONSTANTES
# ══════════════════════════════════════════════════════════════
COLS_INFO = [
    'Aprendiz', 'Correo', 'Numero', 'Ingreso a Zajuna',
    'Ingreso al curso', 'Por Calificar', 'Aprobado',
    'Reprobado', 'Sin Entrega', 'Total', 'Progreso'
]


# ══════════════════════════════════════════════════════════════
# FUNCIONES PRINCIPALES
# ══════════════════════════════════════════════════════════════
def cargar_aprendices(df: pd.DataFrame) -> list:
    """
    Transforma cada fila del Excel en un diccionario de aprendiz.
    Usa un ciclo FOR para recorrer filas y otro para las evidencias.
    """
    cols_ev = [c for c in df.columns if c not in COLS_INFO]
    aprendices = []

    for _, fila in df.iterrows():
        evidencias = []

        # FOR: recorrer cada columna de evidencia
        for nombre_ev in cols_ev:
            codigo = str(fila[nombre_ev]).strip() if pd.notna(fila[nombre_ev]) else ''

            # IF/ELIF/ELSE: traducir código al estado legible
            if codigo == 'A':
                estado = 'Aprobada'
            elif codigo == 'D':
                estado = 'No Aprobada'
            elif codigo in ('SC', 'SN', 'RV', 'BR'):
                estado = 'Sin Calificar'
            elif codigo in ('', 'nan'):
                estado = 'Sin Entrega'
            else:
                estado = codigo

            evidencias.append({'nombre': nombre_ev, 'estado': estado})

        ingreso = fila.get('Ingreso a Zajuna')
        ultimo_ingreso = str(ingreso)[:10] if pd.notna(ingreso) else 'Sin registro'

        aprendices.append({
            'nombre':         str(fila.get('Aprendiz', '')).strip(),
            'documento':      str(fila.get('Numero', '')).strip(),
            'correo':         str(fila.get('Correo', '')).strip(),
            'ultimo_ingreso': ultimo_ingreso,
            'evidencias':     evidencias,
        })

    return aprendices


def clasificar_aprendiz(evidencias: list) -> dict:
    """
    Cuenta evidencias por estado con un FOR y clasifica
    al aprendiz con IF/ELIF/ELSE.
    """
    aprobadas = no_aprobadas = sin_calificar = sin_entrega = 0

    for ev in evidencias:
        if ev['estado'] == 'Aprobada':
            aprobadas += 1
        elif ev['estado'] == 'No Aprobada':
            no_aprobadas += 1
        elif ev['estado'] == 'Sin Calificar':
            sin_calificar += 1
        else:
            sin_entrega += 1

    total = len(evidencias)
    porcentaje = (aprobadas / total * 100) if total > 0 else 0

    # Clasificación IF/ELIF/ELSE
    if no_aprobadas > 0:
        clasificacion = '⚠️ En riesgo de pérdida'
        badge_class   = 'badge-riesgo'
        color_bar     = '#dc3545'
    elif sin_entrega > 3:
        clasificacion = '🔴 Situación crítica'
        badge_class   = 'badge-critico'
        color_bar     = '#6f42c1'
    elif porcentaje >= 90:
        clasificacion = '✅ Aprendiz al día'
        badge_class   = 'badge-ok'
        color_bar     = '#28a745'
    elif porcentaje >= 70:
        clasificacion = '⏳ Con evidencias pendientes'
        badge_class   = 'badge-pend'
        color_bar     = '#ffc107'
    else:
        clasificacion = '🔴 Situación crítica'
        badge_class   = 'badge-critico'
        color_bar     = '#6f42c1'

    return {
        'clasificacion': clasificacion,
        'badge_class':   badge_class,
        'color_bar':     color_bar,
        'aprobadas':     aprobadas,
        'no_aprobadas':  no_aprobadas,
        'sin_calificar': sin_calificar,
        'sin_entrega':   sin_entrega,
        'porcentaje':    porcentaje,
    }


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/"
        "Sena_colombia_logo.svg/200px-Sena_colombia_logo.svg.png",
        width=120,
    )
    st.markdown("## 📂 Cargar archivo")
    st.markdown("Sube el reporte exportado desde **Zajuna** en formato `.xlsx`")

    archivo = st.file_uploader(
        "Archivo Excel de Zajuna",
        type=["xlsx"],
        label_visibility="collapsed",
    )

    if archivo:
        st.success("✅ Archivo cargado")

    st.markdown("---")
    st.markdown("**🔎 Buscar aprendiz**")
    doc_buscar = st.text_input(
        "Número de documento",
        placeholder="Ej: 1031169077",
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        "<small style='opacity:.6'>Sistema Zajuna · SENA<br>"
        "Desarrollado con Python + Streamlit<br>"
        "Instructora: Isabel Cristina Vivas</small>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════
# PANTALLA PRINCIPAL
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="main-title">🎓 Sistema de Seguimiento de Evidencias</div>', unsafe_allow_html=True)
st.markdown('<div class="main-sub">Plataforma Zajuna · SENA · Ficha de aprendices</div>', unsafe_allow_html=True)

# ── Sin archivo ───────────────────────────────────────────────
if not archivo:
    st.info("👈 **Sube el archivo Excel de Zajuna** en el panel izquierdo para comenzar.")
    st.markdown("""
    ### ¿Cómo usar esta aplicación?
    1. Exporta el reporte de tu ficha desde **Zajuna** en formato `.xlsx`
    2. Cárgalo en el panel lateral izquierdo
    3. Explora el **reporte general** del grupo o busca un aprendiz por documento

    ### ¿Qué hace el sistema?
    - 📊 Clasifica a cada aprendiz como: *Al día*, *Pendiente*, *En riesgo* o *Crítico*
    - 🔍 Muestra solo las evidencias que requieren atención
    - 📈 Calcula estadísticas globales del grupo
    - 📥 Permite descargar el reporte en Excel
    """)
    st.stop()

# ── Leer y procesar Excel ─────────────────────────────────────
try:
    df = pd.read_excel(archivo, header=3)
    aprendices = cargar_aprendices(df)
except Exception as e:
    st.error(f"❌ Error al leer el archivo: {e}")
    st.stop()

# ══════════════════════════════════════════════════════════════
# ESTADÍSTICAS GLOBALES (métricas en cards)
# ══════════════════════════════════════════════════════════════
resultados = [clasificar_aprendiz(a['evidencias']) for a in aprendices]

total_ap  = sum(r['aprobadas']     for r in resultados)
total_no  = sum(r['no_aprobadas']  for r in resultados)
total_sc  = sum(r['sin_calificar'] for r in resultados)
total_se  = sum(r['sin_entrega']   for r in resultados)
gran_tot  = total_ap + total_no + total_sc + total_se
pct_global = (total_ap / gran_tot * 100) if gran_tot > 0 else 0

al_dia    = sum(1 for r in resultados if '✅' in r['clasificacion'])
en_riesgo = sum(1 for r in resultados if '⚠️' in r['clasificacion'])
critico   = sum(1 for r in resultados if '🔴' in r['clasificacion'])
pendiente = sum(1 for r in resultados if '⏳' in r['clasificacion'])

st.markdown('<hr class="sena-divider">', unsafe_allow_html=True)
st.markdown("### 📊 Resumen del grupo")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("👥 Total aprendices", len(aprendices))
c2.metric("✅ Al día",           al_dia)
c3.metric("⏳ Pendientes",       pendiente)
c4.metric("⚠️ En riesgo",        en_riesgo)
c5.metric("🔴 Críticos",         critico)

st.markdown("**% Aprobación global del grupo**")
prog_pct = round(pct_global, 1)
color_prog = '#28a745' if pct_global >= 70 else ('#ffc107' if pct_global >= 50 else '#dc3545')
st.markdown(f"""
<div class="prog-bar-wrap">
  <div class="prog-bar-fill" style="width:{prog_pct}%;background:{color_prog};"></div>
</div>
<small style="color:#6c757d">{prog_pct}% · {total_ap:,} evidencias aprobadas de {gran_tot:,} totales</small>
""", unsafe_allow_html=True)

st.markdown('<hr class="sena-divider">', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# TABS: Reporte general / Buscar aprendiz / Descargar
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["📋 Reporte general", "🔍 Buscar aprendiz", "📥 Descargar reporte"])


# ── TAB 1: Reporte general ────────────────────────────────────
with tab1:
    st.markdown("### Listado completo de aprendices")

    # Filtros
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        filtro_texto = st.text_input("🔎 Filtrar por nombre", placeholder="Escribe un nombre...")
    with col_f2:
        filtro_estado = st.selectbox(
            "Filtrar por estado",
            ["Todos", "✅ Al día", "⏳ Pendientes", "⚠️ En riesgo", "🔴 Crítico"]
        )

    # Ordenar por % aprobación descendente
    pares = list(zip(aprendices, resultados))
    pares.sort(key=lambda x: x[1]['porcentaje'], reverse=True)

    mostrados = 0
    for aprendiz, res in pares:
        # Aplicar filtros
        if filtro_texto and filtro_texto.lower() not in aprendiz['nombre'].lower():
            continue
        if filtro_estado != "Todos" and filtro_estado not in res['clasificacion']:
            continue

        mostrados += 1
        pct  = res['porcentaje']
        col_bar = res['color_bar']

        st.markdown(f"""
        <div class="aprendiz-card">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <div>
              <strong style="font-size:15px;">{aprendiz['nombre']}</strong>
              <span style="color:#6c757d;font-size:12px;margin-left:10px;">
                Doc: {aprendiz['documento']} · Último ingreso: {aprendiz['ultimo_ingreso']}
              </span>
            </div>
            <span class="badge {res['badge_class']}">{res['clasificacion']}</span>
          </div>
          <div style="display:flex;gap:20px;font-size:12px;color:#555;margin-bottom:8px;">
            <span>✅ Aprobadas: <strong>{res['aprobadas']}</strong></span>
            <span>❌ No aprobadas: <strong>{res['no_aprobadas']}</strong></span>
            <span>⏳ Sin calificar: <strong>{res['sin_calificar']}</strong></span>
            <span>📭 Sin entrega: <strong>{res['sin_entrega']}</strong></span>
          </div>
          <div class="prog-bar-wrap">
            <div class="prog-bar-fill" style="width:{pct:.1f}%;background:{col_bar};"></div>
          </div>
          <small style="color:#6c757d;">{pct:.1f}% de aprobación</small>
        </div>
        """, unsafe_allow_html=True)

    if mostrados == 0:
        st.warning("No se encontraron aprendices con esos filtros.")


# ── TAB 2: Buscar aprendiz ────────────────────────────────────
with tab2:
    st.markdown("### Consulta individual por documento")

    doc_input = st.text_input(
        "Número de documento del aprendiz",
        value=doc_buscar,
        placeholder="Ej: 1031169077",
        key="buscar_doc"
    )

    if doc_input:
        encontrados = [
            (a, clasificar_aprendiz(a['evidencias']))
            for a in aprendices
            if doc_input.strip().lower() in a['documento'].lower()
        ]

        if not encontrados:
            st.error("⚠️ No se encontró ningún aprendiz con ese documento.")
        else:
            for aprendiz, res in encontrados:
                pct = res['porcentaje']
                col_bar = res['color_bar']

                st.markdown(f"""
                <div class="aprendiz-card" style="border-left:4px solid {col_bar};">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                      <div style="font-size:20px;font-weight:700;color:#003820;">
                        {aprendiz['nombre']}
                      </div>
                      <div style="font-size:13px;color:#6c757d;margin-top:4px;">
                        📄 {aprendiz['documento']} &nbsp;|&nbsp;
                        📧 {aprendiz['correo']} &nbsp;|&nbsp;
                        🕐 Último ingreso: {aprendiz['ultimo_ingreso']}
                      </div>
                    </div>
                    <span class="badge {res['badge_class']}" style="font-size:14px;padding:6px 14px;">
                      {res['clasificacion']}
                    </span>
                  </div>
                  <hr style="margin:14px 0;border-color:#f0f0f0;">
                  <div style="display:flex;gap:24px;font-size:13px;">
                    <span>✅ <strong>{res['aprobadas']}</strong> aprobadas</span>
                    <span>❌ <strong>{res['no_aprobadas']}</strong> no aprobadas</span>
                    <span>⏳ <strong>{res['sin_calificar']}</strong> sin calificar</span>
                    <span>📭 <strong>{res['sin_entrega']}</strong> sin entrega</span>
                  </div>
                  <div style="margin-top:12px;">
                    <div class="prog-bar-wrap">
                      <div class="prog-bar-fill" style="width:{pct:.1f}%;background:{col_bar};"></div>
                    </div>
                    <small style="color:#6c757d;">{pct:.1f}% de aprobación</small>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                # Evidencias pendientes
                pendientes = [ev for ev in aprendiz['evidencias'] if ev['estado'] != 'Aprobada']
                if pendientes:
                    with st.expander(f"⚠️ Ver {len(pendientes)} evidencias que requieren atención"):
                        for ev in pendientes:
                            if ev['estado'] == 'No Aprobada':
                                icono, color = '❌', '#dc3545'
                            elif ev['estado'] == 'Sin Calificar':
                                icono, color = '⏳', '#856404'
                            else:
                                icono, color = '📭', '#6c757d'

                            st.markdown(f"""
                            <div class="ev-row">
                              <span>{icono} {ev['nombre'][:70]}</span>
                              <span style="color:{color};font-weight:500;font-size:12px;">
                                {ev['estado']}
                              </span>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.success("🎉 ¡Todas las evidencias están aprobadas!")
    else:
        st.info("👆 Escribe un número de documento para buscar un aprendiz.")


# ── TAB 3: Descargar reporte ──────────────────────────────────
with tab3:
    st.markdown("### Descargar reporte en Excel")
    st.markdown("Genera un archivo `.xlsx` con el resumen completo del grupo.")

    filas = []
    for aprendiz, res in zip(aprendices, resultados):
        filas.append({
            'Nombre':          aprendiz['nombre'],
            'Documento':       aprendiz['documento'],
            'Correo':          aprendiz['correo'],
            'Último ingreso':  aprendiz['ultimo_ingreso'],
            'Aprobadas':       res['aprobadas'],
            'No aprobadas':    res['no_aprobadas'],
            'Sin calificar':   res['sin_calificar'],
            'Sin entrega':     res['sin_entrega'],
            '% Aprobación':    round(res['porcentaje'], 1),
            'Clasificación':   res['clasificacion'],
        })

    df_reporte = pd.DataFrame(filas)

    buf = BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df_reporte.to_excel(writer, index=False, sheet_name='Reporte')
    buf.seek(0)

    st.dataframe(df_reporte, use_container_width=True)

    st.download_button(
        label="📥 Descargar reporte Excel",
        data=buf,
        file_name="reporte_zajuna.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
