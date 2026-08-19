import os
import subprocess

# Carpeta que contiene los archivos .doc y .docx
carpeta = "documentos"
salida = "pdfs"

# Crear carpeta de salida si no existe
os.makedirs(salida, exist_ok=True)

# Iterar sobre los archivos
for archivo in os.listdir(carpeta):
    if archivo.endswith(".doc") or archivo.endswith(".docx"):
        ruta_entrada = os.path.join(carpeta, archivo)
        comando = [
            "soffice",  # LibreOffice CLI
            "--headless",
            "--convert-to", "pdf",
            "--outdir", salida,
            ruta_entrada
        ]
        subprocess.run(comando)

print("Conversión completada.")
