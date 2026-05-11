# 🎓 Sistema de Seguimiento de Evidencias – Zajuna SENA

Aplicación web desarrollada en **Python + Streamlit** para el seguimiento académico de aprendices del SENA a través de la plataforma Zajuna.

## ¿Qué hace?

- 📂 **Carga** el reporte Excel exportado desde Zajuna
- 📊 **Clasifica** automáticamente a cada aprendiz: *Al día*, *Pendiente*, *En riesgo* o *Crítico*
- 🔍 **Consulta** individual por número de documento
- 📈 **Estadísticas globales** del grupo con barra de progreso
- 📥 **Descarga** el reporte procesado en Excel

## Estructura del repositorio

```
zajuna_app/
│
├── app.py              # Aplicación principal Streamlit
├── requirements.txt    # Dependencias
└── README.md           # Este archivo
```

## Cómo ejecutar localmente

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/zajuna-app.git
cd zajuna-app

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la app
streamlit run app.py
```

## Cómo desplegar en Streamlit Cloud

1. Sube este repositorio a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu cuenta de GitHub
4. Selecciona el repositorio y el archivo `app.py`
5. Haz clic en **Deploy** ✅

## Formato del archivo Excel

El archivo debe ser el reporte exportado directamente desde Zajuna. El sistema espera:
- Encabezados en la **fila 4** (índice 3)
- Columnas de información: `Aprendiz`, `Correo`, `Numero`, `Ingreso a Zajuna`, etc.
- Columnas de evidencias con códigos: `A` (Aprobada), `D` (No aprobada), `SC` (Sin calificar)

## Tecnologías

- [Python 3.10+](https://python.org)
- [Streamlit](https://streamlit.io)
- [Pandas](https://pandas.pydata.org)
- [OpenPyXL](https://openpyxl.readthedocs.io)

## Autora

**Isabel Cristina Vivas** · Instructora SENA  
Universidad de Bogotá Jorge Tadeo Lozano · Mayo 2026
