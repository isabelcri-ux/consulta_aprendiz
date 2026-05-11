import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(page_title="Sistema Zajuna · SENA", page_icon="🎓",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ══ BASE: fondo blanco, texto negro, modo claro forzado ══ */
html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
.main,
.block-container { background-color: #ffffff !important; }

/* Todo el texto del área principal en oscuro por defecto */
body, .main, .block-container,
.main *, .block-container * {
    font-family: 'Inter', sans-serif;
    color: #1a1a1a;
}

/* ══ SIDEBAR: verde oscuro con texto blanco ══ */
[data-testid="stSidebar"],
[data-testid="stSidebar"] * {
    background-color: transparent;
    color: #ffffff !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #003820 0%, #00582E 100%) !important;
}

/* ══ TABS ══ */
[data-testid="stTabs"] button { color: #333333 !important; font-weight: 500; }
[data-testid="stTabs"] button[aria-selected="true"] { color: #003820 !important; font-weight: 700; }

/* ══ INPUTS ══ */
[data-testid="stSelectbox"] label,
[data-testid="stTextInput"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stFileUploader"] label { color: #1a1a1a !important; }
input, select, textarea { color: #1a1a1a !important; }

/* ══ MÉTRICAS (no usadas pero por si acaso) ══ */
[data-testid="stMetricValue"] { color: #1a1a1a !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #555555 !important; }

/* ══ ALERTAS ══ */
/* Alertas en área principal: texto oscuro */
[data-testid="stAlert"]:not([data-testid="stSidebar"] *) * { color: #1a1a1a !important; }
/* Alertas dentro del sidebar: texto blanco */
[data-testid="stSidebar"] [data-testid="stAlert"] * { color: #ffffff !important; }
[data-testid="stSidebar"] [data-testid="stAlert"] { background: rgba(255,255,255,0.15) !important; border-color: rgba(255,255,255,0.3) !important; }

/* ══ TARJETA REPORTE GENERAL ══ */
.aprendiz-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 16px 20px;
    border: 1px solid #e0e0e0;
    margin-bottom: 10px;
}

/* ══ DASHBOARD HEADER (fondo verde → texto blanco) ══ */
.dash-header { background: linear-gradient(135deg,#003820 0%,#00733A 100%); border-radius:16px; padding:28px 32px; margin-bottom:20px; }
.dash-header * { color: #ffffff !important; }
.dash-name  { font-size:24px; font-weight:700; }
.dash-meta  { font-size:13px; opacity:.85; }
.dash-pct   { font-size:52px; font-weight:800; line-height:1; }
.dash-pct-label { font-size:13px; opacity:.85; margin-top:4px; }

/* ══ STAT CARDS DEL DASHBOARD ══ */
.stat-card { background:#ffffff; border-radius:12px; padding:18px 20px; border:1px solid #e0e0e0; text-align:center; }
.stat-num  { font-size:2.2rem; font-weight:800; line-height:1; }
.stat-label { font-size:12px; color:#555555 !important; margin-top:4px; }

/* ══ BADGES ══ */
.badge         { display:inline-block; padding:5px 14px; border-radius:99px; font-size:13px; font-weight:600; }
.badge-ok      { background:#d4edda; color:#155724 !important; }
.badge-pend    { background:#fff3cd; color:#856404 !important; }
.badge-riesgo  { background:#f8d7da; color:#721c24 !important; }
.badge-critico { background:#e2d9f3; color:#432874 !important; }

/* ══ BARRAS DE PROGRESO ══ */
.prog-bar-wrap { background:#e9ecef; border-radius:99px; height:10px; width:100%; overflow:hidden; margin-bottom:4px; }
.prog-bar-fill { height:10px; border-radius:99px; }

/* ══ DIVISOR ══ */
.sena-divider { border:none; border-top:2px solid #00582E; margin:24px 0 20px; opacity:.15; }

/* ══ BOTÓN COLAPSAR SIDEBAR (flecha) ══ */
[data-testid="collapsedControl"],
button[kind="header"],
[data-testid="stSidebarCollapsedControl"] {
    background-color: #003820 !important;
    border-radius: 0 8px 8px 0 !important;
    border: none !important;
}
[data-testid="collapsedControl"] svg,
[data-testid="stSidebarCollapsedControl"] svg,
button[kind="header"] svg {
    fill: #ffffff !important;
    color: #ffffff !important;
}
/* Botón expandir/colapsar dentro del sidebar */
[data-testid="stSidebar"] button {
    background: rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] button svg {
    fill: #ffffff !important;
    color: #ffffff !important;
}
/* Garantizar que la flecha ">>" sea visible */
[data-testid="stSidebarCollapseButton"] {
    background: #003820 !important;
}
[data-testid="stSidebarCollapseButton"] svg {
    fill: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

COLS_INFO = ['Aprendiz','Correo','Numero','Ingreso a Zajuna','Ingreso al curso',
             'Por Calificar','Aprobado','Reprobado','Sin Entrega','Total','Progreso']

def cargar_aprendices(df):
    cols_ev = [c for c in df.columns if c not in COLS_INFO]
    aprendices = []
    for _, fila in df.iterrows():
        evidencias = []
        for nombre_ev in cols_ev:
            codigo = str(fila[nombre_ev]).strip() if pd.notna(fila[nombre_ev]) else ''
            if codigo == 'A':             estado = 'Aprobada'
            elif codigo == 'D':           estado = 'No Aprobada'
            elif codigo in ('SC','SN','RV','BR'): estado = 'Sin Calificar'
            elif codigo in ('','nan'):    estado = 'Sin Entrega'
            else:                         estado = codigo
            evidencias.append({'nombre': nombre_ev, 'estado': estado})
        ingreso = fila.get('Ingreso a Zajuna')
        ultimo_ingreso = str(ingreso)[:10] if pd.notna(ingreso) else 'Sin registro'
        aprendices.append({
            'nombre':         str(fila.get('Aprendiz','')).strip(),
            'documento':      str(fila.get('Numero','')).strip(),
            'correo':         str(fila.get('Correo','')).strip(),
            'ultimo_ingreso': ultimo_ingreso,
            'evidencias':     evidencias,
        })
    return aprendices

def clasificar_aprendiz(evidencias):
    aprobadas = no_aprobadas = sin_calificar = sin_entrega = 0
    for ev in evidencias:
        if ev['estado'] == 'Aprobada':          aprobadas += 1
        elif ev['estado'] == 'No Aprobada':     no_aprobadas += 1
        elif ev['estado'] == 'Sin Calificar':   sin_calificar += 1
        else:                                   sin_entrega += 1
    total = len(evidencias)
    pct = (aprobadas / total * 100) if total > 0 else 0
    if no_aprobadas > 0:
        cl,bc,cb = '⚠️ En riesgo de pérdida','badge-riesgo','#dc3545'
    elif sin_entrega > 3:
        cl,bc,cb = '🔴 Situación crítica','badge-critico','#6f42c1'
    elif pct >= 90:
        cl,bc,cb = '✅ Aprendiz al día','badge-ok','#28a745'
    elif pct >= 70:
        cl,bc,cb = '⏳ Con evidencias pendientes','badge-pend','#ffc107'
    else:
        cl,bc,cb = '🔴 Situación crítica','badge-critico','#6f42c1'
    return {'clasificacion':cl,'badge_class':bc,'color_bar':cb,
            'aprobadas':aprobadas,'no_aprobadas':no_aprobadas,
            'sin_calificar':sin_calificar,'sin_entrega':sin_entrega,'porcentaje':pct}

# ── Gráficas ────────────────────────────────────────────────
# Color base para todos los textos de gráficas
TEXT_COLOR  = '#1a1a1a'
FONT_FAMILY = 'Inter'

def fig_dona(res):
    fig = go.Figure(go.Pie(
        labels=['Aprobadas','No Aprobadas','Sin Calificar','Sin Entrega'],
        values=[res['aprobadas'],res['no_aprobadas'],res['sin_calificar'],res['sin_entrega']],
        hole=.65,
        marker=dict(colors=['#28a745','#dc3545','#ffc107','#adb5bd'],
                    line=dict(color='white',width=2)),
        textinfo='percent',
        textfont=dict(size=12, family=FONT_FAMILY, color=TEXT_COLOR),
        hovertemplate='<b>%{label}</b><br>%{value} evidencias<br>%{percent}<extra></extra>',
    ))
    fig.add_annotation(
        text=f"<b>{res['porcentaje']:.0f}%</b><br><span style='font-size:11px'>aprobación</span>",
        x=0.5, y=0.5,
        font=dict(size=18, color='#003820', family=FONT_FAMILY),
        showarrow=False, align='center')
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation='h', yanchor='bottom', y=-0.35,
            xanchor='center', x=0.5,
            font=dict(size=11, family=FONT_FAMILY, color=TEXT_COLOR),
        ),
        margin=dict(t=10, b=60, l=10, r=10), height=300,
        paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
    )
    return fig

def fig_barras(res):
    fig = go.Figure(go.Bar(
        x=[res['aprobadas'],res['sin_calificar'],res['no_aprobadas'],res['sin_entrega']],
        y=['Aprobadas','Sin Calificar','No Aprobadas','Sin Entrega'],
        orientation='h',
        marker=dict(color=['#28a745','#ffc107','#dc3545','#adb5bd'],
                    line=dict(color='white', width=1)),
        text=[res['aprobadas'],res['sin_calificar'],res['no_aprobadas'],res['sin_entrega']],
        textposition='outside',
        textfont=dict(size=13, family=FONT_FAMILY, color=TEXT_COLOR),
        hovertemplate='<b>%{y}</b>: %{x}<extra></extra>',
    ))
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=50), height=230,
        paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
        xaxis=dict(showgrid=True, gridcolor='#eeeeee', zeroline=False,
                   tickfont=dict(size=11, color=TEXT_COLOR)),
        yaxis=dict(showgrid=False,
                   tickfont=dict(size=12, family=FONT_FAMILY, color=TEXT_COLOR)),
        bargap=.35,
    )
    return fig

def fig_gauge(pct, color):
    fig = go.Figure(go.Indicator(
        mode='gauge+number', value=round(pct, 1),
        number=dict(suffix='%', font=dict(size=36, color=color, family=FONT_FAMILY)),
        gauge=dict(
            axis=dict(range=[0,100], tickwidth=1, tickcolor='#999',
                      tickfont=dict(size=10, family=FONT_FAMILY, color=TEXT_COLOR)),
            bar=dict(color=color, thickness=0.25),
            bgcolor='white', borderwidth=0,
            steps=[
                dict(range=[0,  50], color='#fdf0f0'),
                dict(range=[50, 70], color='#fffbea'),
                dict(range=[70, 90], color='#edf6ea'),
                dict(range=[90,100], color='#d4edda'),
            ],
            threshold=dict(line=dict(color='#003820',width=3), thickness=0.8, value=pct),
        )))
    fig.update_layout(
        margin=dict(t=20, b=10, l=20, r=20), height=230,
        paper_bgcolor='#ffffff',
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
    )
    return fig

def fig_comparativa(nombre_sel, aprendices, resultados):
    nombres = [a['nombre'].split()[0]+' '+a['nombre'].split()[-1] for a in aprendices]
    porcs   = [r['porcentaje'] for r in resultados]
    colores = ['#003820' if a['nombre']==nombre_sel else '#81C784' for a in aprendices]
    pares   = sorted(zip(nombres,porcs,colores), key=lambda x:x[1], reverse=True)
    n, p, c = zip(*pares)
    # Color de texto de cada barra: blanco si es la seleccionada, oscuro si no
    text_colors = ['#ffffff' if col=='#003820' else TEXT_COLOR for col in c]
    fig = go.Figure(go.Bar(
        x=list(n), y=list(p),
        marker=dict(color=list(c), line=dict(color='white', width=1)),
        text=[f"{v:.0f}%" for v in p],
        textposition='outside',
        textfont=dict(size=11, family=FONT_FAMILY, color=TEXT_COLOR),
        hovertemplate='<b>%{x}</b><br>Aprobación: %{y:.1f}%<extra></extra>',
    ))
    promedio = sum(porcs)/len(porcs)
    fig.add_hline(
        y=promedio, line_dash='dot', line_color='#dc3545',
        annotation_text=f'Promedio: {promedio:.1f}%',
        annotation_position='top right',
        annotation_font=dict(size=11, color='#dc3545', family=FONT_FAMILY),
    )
    fig.update_layout(
        margin=dict(t=40, b=80, l=10, r=20), height=360,
        paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
        font=dict(color=TEXT_COLOR, family=FONT_FAMILY),
        xaxis=dict(
            tickangle=-40,
            tickfont=dict(size=10, family=FONT_FAMILY, color=TEXT_COLOR),
            showgrid=False,
        ),
        yaxis=dict(
            showgrid=True, gridcolor='#eeeeee',
            range=[0, 115],
            ticksuffix='%',
            tickfont=dict(size=10, family=FONT_FAMILY, color=TEXT_COLOR),
        ),
        bargap=.25,
    )
    return fig

# ── Dashboard individual ─────────────────────────────────────
def mostrar_dashboard(aprendiz, res, todos_aprendices, todos_resultados):
    pct = res['porcentaje']
    cb  = res['color_bar']

    st.markdown(f"""
    <div class="dash-header">
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;">
        <div>
          <div style="font-size:24px;font-weight:700;color:#ffffff;margin-bottom:4px;">🎓 {aprendiz['nombre']}</div>
          <div class="dash-meta">📄 {aprendiz['documento']} &nbsp;·&nbsp; 📧 {aprendiz['correo']} &nbsp;·&nbsp; 🕐 {aprendiz['ultimo_ingreso']}</div>
          <div style="margin-top:12px;"><span class="badge {res['badge_class']}">{res['clasificacion']}</span></div>
        </div>
        <div style="text-align:right;">
          <div class="dash-pct">{pct:.1f}%</div>
          <div class="dash-pct-label">porcentaje de aprobación</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    for col,num,label,color in [
        (c1,res['aprobadas'],'✅ Aprobadas','#28a745'),
        (c2,res['sin_calificar'],'⏳ Sin calificar','#ffc107'),
        (c3,res['no_aprobadas'],'❌ No aprobadas','#dc3545'),
        (c4,res['sin_entrega'],'📭 Sin entrega','#adb5bd'),
    ]:
        with col:
            st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:{color};">{num}</div><div class="stat-label">{label}</div></div>',
                        unsafe_allow_html=True)

    st.markdown('<hr class="sena-divider">', unsafe_allow_html=True)

    st.markdown("<h4 style='color:#1a1a1a;font-weight:600;'>📊 Distribución de evidencias</h4>", unsafe_allow_html=True)
    cd,cb2,cg = st.columns([1.2,1.2,1])
    with cd:
        st.markdown("<p style='color:#1a1a1a;font-weight:600;margin-bottom:4px;'>Dona por estado</p>", unsafe_allow_html=True)
        st.plotly_chart(fig_dona(res), use_container_width=True, config={'displayModeBar':False})
    with cb2:
        st.markdown("<p style='color:#1a1a1a;font-weight:600;margin-bottom:4px;'>Conteo por categoría</p>", unsafe_allow_html=True)
        st.plotly_chart(fig_barras(res), use_container_width=True, config={'displayModeBar':False})
    with cg:
        st.markdown("<p style='color:#1a1a1a;font-weight:600;margin-bottom:4px;'>Velocímetro</p>", unsafe_allow_html=True)
        st.plotly_chart(fig_gauge(pct,cb), use_container_width=True, config={'displayModeBar':False})

    st.markdown('<hr class="sena-divider">', unsafe_allow_html=True)
    st.markdown("<h4 style='color:#1a1a1a;font-weight:600;'>📈 Posición en el grupo</h4>", unsafe_allow_html=True)
    promedio = sum(r['porcentaje'] for r in todos_resultados)/len(todos_resultados)
    diff = pct - promedio
    color_d = '#28a745' if diff>=0 else '#dc3545'
    st.markdown(f"El aprendiz está <span style='color:{color_d};font-weight:600;'>{'🔺' if diff>=0 else '🔻'} {abs(diff):.1f}% {'por encima' if diff>=0 else 'por debajo'}</span> del promedio del grupo ({promedio:.1f}%)", unsafe_allow_html=True)
    st.plotly_chart(fig_comparativa(aprendiz['nombre'],todos_aprendices,todos_resultados),
                    use_container_width=True, config={'displayModeBar':False})

    st.markdown('<hr class="sena-divider">', unsafe_allow_html=True)
    pendientes = [ev for ev in aprendiz['evidencias'] if ev['estado'] != 'Aprobada']
    if pendientes:
        st.markdown(f"#### ⚠️ Evidencias que requieren atención ({len(pendientes)})")
        tipos = sorted({ev['estado'] for ev in pendientes})
        filtro = st.multiselect("Filtrar por estado", tipos, default=tipos, key=f"f_{aprendiz['documento']}")
        for ev in [e for e in pendientes if e['estado'] in filtro]:
            if ev['estado']=='No Aprobada':   ico,col,bg='❌','#721c24','#f8d7da'
            elif ev['estado']=='Sin Calificar': ico,col,bg='⏳','#856404','#fff3cd'
            else:                               ico,col,bg='📭','#555','#f1f3f5'
            nombre_ev = ev["nombre"][:80]
            estado_ev = ev["estado"]
            st.markdown(
                f'''<div style="display:flex;justify-content:space-between;align-items:center;
                         padding:10px 14px;border-radius:8px;margin-bottom:5px;
                         background-color:{bg};border-left:4px solid {col};">
                  <span style="flex:1;font-size:13px;font-weight:500;
                               color:#1a1a1a;">{ico}&nbsp;&nbsp;{nombre_ev}</span>
                  <span style="font-size:12px;font-weight:700;color:{col};
                               white-space:nowrap;margin-left:14px;">{estado_ev}</span>
                </div>''',
                unsafe_allow_html=True)
    else:
        st.success("🎉 ¡Todas las evidencias están aprobadas!")

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
      <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="48" height="48" rx="10" fill="#00A550"/>
        <text x="24" y="32" text-anchor="middle"
              font-family="Inter,Arial,sans-serif"
              font-size="18" font-weight="800" fill="#ffffff">SENA</text>
      </svg>
      <div>
        <div style="color:#ffffff;font-weight:700;font-size:15px;line-height:1.2;">SENA</div>
        <div style="color:rgba(255,255,255,0.75);font-size:11px;">Sistema Zajuna</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("## 📂 Cargar archivo")
    archivo = st.file_uploader("Excel de Zajuna", type=["xlsx"], label_visibility="collapsed")
    if archivo:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.18);border:1px solid rgba(255,255,255,0.4);
                    border-radius:10px;padding:10px 14px;margin-top:4px;
                    display:flex;align-items:center;gap:10px;">
          <span style="font-size:20px;">✅</span>
          <div>
            <div style="color:#ffffff;font-weight:700;font-size:13px;">Archivo cargado</div>
            <div style="color:rgba(255,255,255,0.80);font-size:11px;">Listo para procesar</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<small style='opacity:.6'>Sistema Zajuna · SENA<br>Python · Streamlit · Plotly<br>Instructora: Isabel Cristina Vivas</small>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div style="
    padding: 28px 32px;
    background: linear-gradient(135deg, #003820 0%, #005C30 60%, #007A3D 100%);
    border-radius: 16px;
    margin-bottom: 24px;
    border: 1px solid #00A550;
    box-shadow: 0 4px 24px rgba(0,88,46,0.25);
">
    <div style="font-size:2rem;font-weight:800;color:#FFFFFF;letter-spacing:-0.5px;margin-bottom:6px;">
        🎓 Sistema de Seguimiento de Evidencias
    </div>
    <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
        <span style="background:rgba(255,255,255,0.18);color:#ffffff;font-size:12px;
                     font-weight:600;padding:3px 10px;border-radius:99px;letter-spacing:0.04em;">
            PLATAFORMA ZAJUNA
        </span>
        <span style="background:rgba(255,255,255,0.18);color:#ffffff;font-size:12px;
                     font-weight:600;padding:3px 10px;border-radius:99px;letter-spacing:0.04em;">
            SENA
        </span>
        <span style="color:rgba(255,255,255,0.80);font-size:13px;">
            Seguimiento de evidencias de aprendizaje
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

if not archivo:
    st.info("👈 **Sube el archivo Excel de Zajuna** en el panel izquierdo para comenzar.")
    st.stop()

try:
    df = pd.read_excel(archivo, header=3)
    aprendices = cargar_aprendices(df)
except Exception as e:
    st.error(f"❌ Error al leer el archivo: {e}")
    st.stop()

resultados = [clasificar_aprendiz(a['evidencias']) for a in aprendices]

total_ap=sum(r['aprobadas'] for r in resultados)
total_no=sum(r['no_aprobadas'] for r in resultados)
total_sc=sum(r['sin_calificar'] for r in resultados)
total_se=sum(r['sin_entrega'] for r in resultados)
gran_tot=total_ap+total_no+total_sc+total_se
pct_g=(total_ap/gran_tot*100) if gran_tot>0 else 0
al_dia   =sum(1 for r in resultados if '✅' in r['clasificacion'])
en_riesgo=sum(1 for r in resultados if '⚠️' in r['clasificacion'])
critico  =sum(1 for r in resultados if '🔴' in r['clasificacion'])
pendiente=sum(1 for r in resultados if '⏳' in r['clasificacion'])

st.markdown('<hr class="sena-divider">', unsafe_allow_html=True)
st.markdown("<h3 style='color:#1a1a1a;font-weight:700;margin-bottom:16px;'>📊 Resumen del grupo</h3>", unsafe_allow_html=True)
c1,c2,c3,c4,c5=st.columns(5)
with c1:
    st.markdown(f'''<div class="stat-card" style="border-left:4px solid #003820;">
        <div class="stat-num" style="color:#003820;">{len(aprendices)}</div>
        <div class="stat-label" style="color:#555;">👥 Total aprendices</div>
    </div>''', unsafe_allow_html=True)
with c2:
    st.markdown(f'''<div class="stat-card" style="border-left:4px solid #28a745;">
        <div class="stat-num" style="color:#28a745;">{al_dia}</div>
        <div class="stat-label" style="color:#555;">✅ Al día</div>
    </div>''', unsafe_allow_html=True)
with c3:
    st.markdown(f'''<div class="stat-card" style="border-left:4px solid #ffc107;">
        <div class="stat-num" style="color:#856404;">{pendiente}</div>
        <div class="stat-label" style="color:#555;">⏳ Pendientes</div>
    </div>''', unsafe_allow_html=True)
with c4:
    st.markdown(f'''<div class="stat-card" style="border-left:4px solid #dc3545;">
        <div class="stat-num" style="color:#dc3545;">{en_riesgo}</div>
        <div class="stat-label" style="color:#555;">⚠️ En riesgo</div>
    </div>''', unsafe_allow_html=True)
with c5:
    st.markdown(f'''<div class="stat-card" style="border-left:4px solid #6f42c1;">
        <div class="stat-num" style="color:#6f42c1;">{critico}</div>
        <div class="stat-label" style="color:#555;">🔴 Críticos</div>
    </div>''', unsafe_allow_html=True)
color_p='#28a745' if pct_g>=70 else ('#ffc107' if pct_g>=50 else '#dc3545')
st.markdown(f'<div class="prog-bar-wrap" style="height:10px;margin-top:8px;"><div class="prog-bar-fill" style="width:{pct_g:.1f}%;background:{color_p};"></div></div><small style="color:#6c757d">{pct_g:.1f}% aprobación global · {total_ap:,} de {gran_tot:,} evidencias</small>', unsafe_allow_html=True)
st.markdown('<hr class="sena-divider">', unsafe_allow_html=True)

tab1,tab2,tab3=st.tabs(["📋 Reporte general","🔍 Dashboard por aprendiz","📥 Descargar"])

# TAB 1
with tab1:
    st.markdown("<h3 style='color:#1a1a1a;font-weight:700;margin-bottom:16px;'>Listado completo de aprendices</h3>", unsafe_allow_html=True)
    cf1,cf2=st.columns([2,1])
    with cf1: ft=st.text_input("🔎 Filtrar por nombre",placeholder="Escribe un nombre...")
    with cf2: fe=st.selectbox("Estado",["Todos","✅ Al día","⏳ Pendientes","⚠️ En riesgo","🔴 Crítico"])
    pares=sorted(zip(aprendices,resultados),key=lambda x:x[1]['porcentaje'],reverse=True)
    n=0
    for a,r in pares:
        if ft and ft.lower() not in a['nombre'].lower(): continue
        if fe!="Todos" and fe not in r['clasificacion']: continue
        n+=1
        pct=r['porcentaje']
        st.markdown(f'''
        <div style="background:white;border-radius:12px;padding:16px 20px;
                    border:1px solid #e0e0e0;margin-bottom:10px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <div>
              <strong style="font-size:15px;color:#1a1a1a;font-weight:700;">{a["nombre"]}</strong><br>
              <span style="color:#555555;font-size:12px;">Doc: {a["documento"]} &nbsp;·&nbsp; {a["ultimo_ingreso"]}</span>
            </div>
            <span class="badge {r["badge_class"]}">{r["clasificacion"]}</span>
          </div>
          <div style="display:flex;gap:20px;font-size:12px;color:#333333;margin-bottom:8px;">
            <span>✅ <b>{r["aprobadas"]}</b></span>
            <span>❌ <b>{r["no_aprobadas"]}</b></span>
            <span>⏳ <b>{r["sin_calificar"]}</b></span>
            <span>📭 <b>{r["sin_entrega"]}</b></span>
          </div>
          <div style="background:#e9ecef;border-radius:99px;height:10px;overflow:hidden;margin-bottom:4px;">
            <div style="height:10px;border-radius:99px;width:{pct:.1f}%;background:{r["color_bar"]};"></div>
          </div>
          <small style="color:#555555;">{pct:.1f}% de aprobación</small>
        </div>
        ''', unsafe_allow_html=True)
    if n==0: st.warning("No se encontraron aprendices.")

# TAB 2
with tab2:
    st.markdown("<h3 style='color:#1a1a1a;font-weight:700;margin-bottom:16px;'>🔍 Dashboard individual</h3>", unsafe_allow_html=True)
    nombres_lista=[a['nombre'] for a in aprendices]
    nombre_sel=st.selectbox("Selecciona un aprendiz",nombres_lista)
    st.markdown("<small style='color:#6c757d;'>O busca por documento:</small>",unsafe_allow_html=True)
    doc_in=st.text_input("Documento",placeholder="Ej: 1031169077",label_visibility="collapsed",key="doc_dash")
    if doc_in:
        found=[(a,r) for a,r in zip(aprendices,resultados) if doc_in.strip().lower() in a['documento'].lower()]
        if not found: st.error("⚠️ No se encontró ningún aprendiz con ese documento.")
        else: mostrar_dashboard(found[0][0],found[0][1],aprendices,resultados)
    else:
        idx=nombres_lista.index(nombre_sel)
        mostrar_dashboard(aprendices[idx],resultados[idx],aprendices,resultados)

# TAB 3
with tab3:
    st.markdown("<h3 style='color:#1a1a1a;font-weight:700;margin-bottom:16px;'>📥 Descargar reporte en Excel</h3>", unsafe_allow_html=True)
    filas=[{'Nombre':a['nombre'],'Documento':a['documento'],'Correo':a['correo'],
            'Último ingreso':a['ultimo_ingreso'],'Aprobadas':r['aprobadas'],
            'No aprobadas':r['no_aprobadas'],'Sin calificar':r['sin_calificar'],
            'Sin entrega':r['sin_entrega'],'% Aprobación':round(r['porcentaje'],1),
            'Clasificación':r['clasificacion']} for a,r in zip(aprendices,resultados)]
    df_rep=pd.DataFrame(filas)
    buf=BytesIO()
    with pd.ExcelWriter(buf,engine='openpyxl') as w: df_rep.to_excel(w,index=False,sheet_name='Reporte')
    buf.seek(0)
    st.dataframe(df_rep,use_container_width=True)
    st.download_button("📥 Descargar Excel",data=buf,file_name="reporte_zajuna.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
