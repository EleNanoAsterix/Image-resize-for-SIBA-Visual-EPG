import streamlit as st
from PIL import Image
import os
import zipfile
import shutil
from io import BytesIO

# 📂 Carpeta temporal para imágenes
OUTPUT_FOLDER = "imagenes_redimensionadas"

# Crear carpeta si no existe
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

st.set_page_config(page_title="📷 Redimensionador de Imágenes", layout="centered")
st.title("📷 Redimensionador de Imágenes")
st.write("Sube tus imágenes y las procesaremos según su orientación.")

# 🔹 Botón para limpiar cargas previas
if st.button("🗑 Limpiar imágenes anteriores"):
    shutil.rmtree(OUTPUT_FOLDER)
    os.makedirs(OUTPUT_FOLDER)
    st.success("✅ Imágenes anteriores eliminadas.")

# 📤 Cargar imágenes
uploaded_files = st.file_uploader(
    "Selecciona una o más imágenes", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

# 📌 Procesar imágenes
if uploaded_files:
    total_files = len(uploaded_files)
    progress_bar = st.progress(0)
    processed_files = []

    for i, uploaded_file in enumerate(uploaded_files, start=1):
        img = Image.open(uploaded_file)

        # Verificar orientación y redimensionar
        if img.height > img.width:
            # 📸 Vertical → recortar a 2:3 y redimensionar a 480x720
            target_ratio = 2 / 3
            current_ratio = img.width / img.height
            if current_ratio > target_ratio:  
                new_width = int(img.height * target_ratio)
                left = (img.width - new_width) / 2
                img = img.crop((left, 0, left + new_width, img.height))
            elif current_ratio < target_ratio:
                new_height = int(img.width / target_ratio)
                top = (img.height - new_height) / 2
                img = img.crop((0, top, img.width, top + new_height))
            img_resized = img.resize((480, 720), Image.Resampling.LANCZOS)
            output_path = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(uploaded_file.name)[0]}_480x720.jpg")
            img_resized.save(output_path, "JPEG", quality=100)
            processed_files.append(output_path)

        else:
            # 🖼 Horizontal → recortar a 16:9 y redimensionar a 1920x1080 y 3840x2160
            target_ratio = 16 / 9
            current_ratio = img.width / img.height
            if current_ratio > target_ratio:
                new_width = int(img.height * target_ratio)
                left = (img.width - new_width) / 2
                img = img.crop((left, 0, left + new_width, img.height))
            elif current_ratio < target_ratio:
                new_height = int(img.width / target_ratio)
                top = (img.height - new_height) / 2
                img = img.crop((0, top, img.width, top + new_height))

            # Guardar versiones
            for size in [(1920, 1080), (3840, 2160)]:
                img_resized = img.resize(size, Image.Resampling.LANCZOS)
                output_path = os.path.join(OUTPUT_FOLDER, f"{os.path.splitext(uploaded_file.name)[0]}_{size[0]}x{size[1]}.jpg")
                img_resized.save(output_path, "JPEG", quality=100)
                processed_files.append(output_path)

        # Actualizar barra de progreso
        progress_bar.progress(i / total_files)

    st.success(f"✅ Procesadas {len(processed_files)} imágenes.")

    # 📦 Crear ZIP para descarga
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for file_path in processed_files:
            zipf.write(file_path, os.path.basename(file_path))
    zip_buffer.seek(0)

    st.download_button(
        label="⬇ Descargar imágenes en ZIP",
        data=zip_buffer,
        file_name="imagenes_procesadas.zip",
        mime="application/zip"
    )
