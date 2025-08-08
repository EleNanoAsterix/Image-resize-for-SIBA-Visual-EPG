import streamlit as st
import os
import zipfile
from PIL import Image
import shutil

def recortar_a_proporcion(img, proporcion_objetivo):
    """Recorta la imagen centrada a la proporción deseada."""
    ancho_original, alto_original = img.size
    ratio_objetivo = proporcion_objetivo[0] / proporcion_objetivo[1]
    ratio_actual = ancho_original / alto_original

    if ratio_actual > ratio_objetivo:
        nuevo_ancho = int(alto_original * ratio_objetivo)
        izquierda = (ancho_original - nuevo_ancho) // 2
        derecha = izquierda + nuevo_ancho
        caja = (izquierda, 0, derecha, alto_original)
    else:
        nuevo_alto = int(ancho_original / ratio_objetivo)
        arriba = (alto_original - nuevo_alto) // 2
        abajo = arriba + nuevo_alto
        caja = (0, arriba, ancho_original, abajo)

    return img.crop(caja)

def redimensionar_y_guardar(img, tamaño, nombre_base, sufijo, carpeta_salida):
    """Redimensiona y guarda la imagen como JPG (calidad 95%)."""
    img_redimensionada = img.resize(tamaño, Image.LANCZOS)
    nombre_archivo = f"{nombre_base}_{sufijo}.jpg"
    ruta_salida = os.path.join(carpeta_salida, nombre_archivo)
    img_redimensionada.save(ruta_salida, format='JPEG', quality=95, subsampling=0)
    return nombre_archivo


def crear_zip(carpeta, nombre_zip):
    """Crea un archivo ZIP con todas las imágenes de la carpeta."""
    ruta_zip = os.path.join(carpeta, nombre_zip)
    with zipfile.ZipFile(ruta_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for archivo in os.listdir(carpeta):
            if archivo != nombre_zip:
                zipf.write(os.path.join(carpeta, archivo), arcname=archivo)
    return ruta_zip

def limpiar_carpeta(carpeta):
    """Elimina la carpeta si existe."""
    if os.path.exists(carpeta):
        shutil.rmtree(carpeta)

# --- Interfaz Streamlit ---
st.title('📷 Redimensionador de Imágenes Para SIBA Visual EPG')
st.write('Si la imagen es vertical → 480x720 (2:3). Si es horizontal → 1920x1080 y 3840x2160 (16:9).')

carpeta_salida = 'imagenes_redimensionadas'

# Botón para limpiar archivos anteriores
if st.button("🗑 Limpiar archivos anteriores"):
    limpiar_carpeta(carpeta_salida)
    st.success("Archivos anteriores eliminados.")

archivos_subidos = st.file_uploader(
    "Arrastra y suelta tus imágenes aquí",
    type=['png', 'jpg', 'jpeg'],
    accept_multiple_files=True
)

if archivos_subidos:
    if st.button('⚙ Procesar y Descargar ZIP'):
        limpiar_carpeta(carpeta_salida)
        os.makedirs(carpeta_salida, exist_ok=True)
        archivos_generados = []

        progreso = st.progress(0)
        total = len(archivos_subidos)

        for i, archivo in enumerate(archivos_subidos):
            try:
                img = Image.open(archivo)
                nombre_base = os.path.splitext(archivo.name)[0]
                ancho, alto = img.size

                if alto > ancho:
                    # Imagen vertical → 480x720
                    img_2x3 = recortar_a_proporcion(img, (2, 3))
                    archivo_2x3 = redimensionar_y_guardar(img_2x3, (480, 720), nombre_base, '480x720', carpeta_salida)
                    archivos_generados.append(archivo_2x3)
                else:
                    # Imagen horizontal → 1920x1080 y 3840x2160
                    img_16x9 = recortar_a_proporcion(img, (16, 9))
                    archivo_hd = redimensionar_y_guardar(img_16x9, (1920, 1080), nombre_base, '1920x1080', carpeta_salida)
                    archivo_4k = redimensionar_y_guardar(img_16x9, (3840, 2160), nombre_base, '3840x2160', carpeta_salida)
                    archivos_generados.extend([archivo_hd, archivo_4k])

                # Actualizar barra de progreso
                progreso.progress(int(((i + 1) / total) * 100))

            except Exception as e:
                st.error(f"Error procesando {archivo.name}: {e}")

        # Crear ZIP
        nombre_zip = "imagenes_redimensionadas.zip"
        ruta_zip = crear_zip(carpeta_salida, nombre_zip)

        # Descargar ZIP
        with open(ruta_zip, "rb") as f:
            st.download_button(
                label="📦 Descargar todas en ZIP",
                data=f,
                file_name=nombre_zip,
                mime="application/zip"
            )


