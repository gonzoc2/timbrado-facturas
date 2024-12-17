import streamlit as st
import pandas as pd
from io import BytesIO

# Título de la app
st.title('Hacer archivo de Excel 📊')

# Instrucciones para el usuario
st.write("Sube un archivo de Excel para procesarlo y ver su contenido.")

# Inicializar la variable en session_state para almacenar los archivos generados
if 'archivos_generados' not in st.session_state:
    st.session_state['archivos_generados'] = []

# Subir el primer archivo de Excel
archivo1 = st.file_uploader("Sube el archivo de Excel con los datos del proveedor", type=["xlsx", "xls"])

# Verificar si se subió el archivo
if archivo1 is not None:
    if 'archivo_subido' not in st.session_state or st.session_state['archivo_subido'] != archivo1.name:
        try:
            # Leer el archivo de Excel y forzar todas las columnas como texto
            df1 = pd.read_excel(archivo1, dtype=str)

            # Mostrar los primeros 5 registros del archivo
            st.subheader("Contenido del archivo con los datos 📂")
            st.write(df1)

            # Paso 1: Transformar las columnas que contienen "fecha" en su nombre
            fecha_columnas = [col for col in df1.columns if 'fecha' in col.lower()]
            if fecha_columnas:
                for col in fecha_columnas:
                    try:
                        # Convertir la columna al formato deseado
                        df1[col] = pd.to_datetime(df1[col], errors='coerce').dt.strftime('%Y-%m-%dT12:00:00')
                    except Exception as e:
                        st.error(f"No se pudo convertir la columna {col} a formato de fecha: {e}")

            st.subheader("Contenido del archivo con las fechas transformadas 📅")
            st.write(df1)

            # Paso 2: Crear archivos por cada valor único de RFCEMISOR_D y dividir en archivos de 25 filas cada uno
            if 'RFCEMISOR_D' in df1.columns:
                st.subheader("Creación de archivos por RFCEMISOR_D 📦")
                archivos_generados = []  # Lista para almacenar los archivos generados
                
                valores_rfc = df1['RFCEMISOR_D'].unique()
                for rfc in valores_rfc:
                    # Filtrar por cada valor de RFCEMISOR_D
                    df_rfc = df1[df1['RFCEMISOR_D'] == rfc]
                    
                    # Dividir en fragmentos de 25 filas (sin contar el encabezado)
                    for i in range(0, len(df_rfc), 25):
                        fragmento = df_rfc.iloc[i:i+25]
                        nombre_archivo = f"{rfc}_parte_{(i // 25) + 1}.xlsx"
                        
                        # Crear un archivo Excel en memoria
                        with BytesIO() as buffer:
                            fragmento.to_excel(buffer, index=False, engine='openpyxl')
                            buffer.seek(0)
                            archivos_generados.append({
                                'nombre': nombre_archivo,
                                'contenido': buffer.getvalue()
                            })
                
                # Guardar los archivos generados en la sesión para evitar reprocesar
                st.session_state['archivos_generados'] = archivos_generados
                st.session_state['archivo_subido'] = archivo1.name  # Para identificar que es el mismo archivo

                st.success(f"Archivos creados por RFCEMISOR_D y divididos en partes de 25 filas. ¡Listo para descargar! 💾")
        
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

else:
    st.info("Por favor, sube un archivo de Excel para ver su contenido.")

# Verifica si hay archivos generados en session_state
if 'archivos_generados' in st.session_state and st.session_state['archivos_generados']:
    st.subheader("Archivos para descargar 📥")
    
    for archivo in st.session_state['archivos_generados']:
        st.download_button(
            label=f"📥 Descargar {archivo['nombre']}",
            data=archivo['contenido'],
            file_name=archivo['nombre'],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
