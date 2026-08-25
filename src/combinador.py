import os
import fitz  # PyMuPDF
from pathlib import Path

# NIT de la entidad, que forma parte del nombre de los archivos generados
# (OPF_<NIT>_ECA.pdf, etc.). Cada institución tiene el suyo, así que se lee del
# entorno y no va escrito en el código:
#     export NIT_ENTIDAD=900123456
NIT = os.environ.get("NIT_ENTIDAD", "000000000")

# Definición de combinaciones por número de páginas
combinaciones = {
    4: [
        {"ORDEN": [1], f"OPF_{NIT}_ECA": [2], f"PDE_{NIT}_ECA": [3], f"CRC_{NIT}_ECA": [4]}
    ],
    5: [
        {"ORDEN": [1], f"OPF_{NIT}_ECA": [2], f"PDE_{NIT}_ECA": [3, 4], f"CRC_{NIT}_ECA": [5]},
        {"ORDEN": [1], f"OPF_{NIT}_ECA": [2, 3], f"PDE_{NIT}_ECA": [4], f"CRC_{NIT}_ECA": [5]}
    ],
    6: [
        {"ORDEN": [1], f"OPF_{NIT}_ECA": [2], f"PDE_{NIT}_ECA": [3, 4, 5], f"CRC_{NIT}_ECA": [6]},
        {"ORDEN": [1], f"OPF_{NIT}_ECA": [2, 3], f"PDE_{NIT}_ECA": [4, 5], f"CRC_{NIT}_ECA": [6]},
        {"ORDEN": [1], f"OPF_{NIT}_ECA": [2, 3, 4], f"PDE_{NIT}_ECA": [5], f"CRC_{NIT}_ECA": [6]}
    ],
    7: [
        {"ORDEN": [1], f"OPF_{NIT}_ECA": [2], f"PDE_{NIT}_ECA": [3, 4, 5, 6], f"CRC_{NIT}_ECA": [7]},
        {"ORDEN": [1], f"OPF_{NIT}_ECA": [2, 3], f"PDE_{NIT}_ECA": [4, 5, 6], f"CRC_{NIT}_ECA": [7]},
        {"ORDEN": [1], f"OPF_{NIT}_ECA": [2, 3, 4], f"PDE_{NIT}_ECA": [5, 6], f"CRC_{NIT}_ECA": [7]}
    ],
    8: [
        {"ORDEN": [1], f"OPF_{NIT}_ECA": [2], f"PDE_{NIT}_ECA": [3, 4, 5, 6, 7], f"CRC_{NIT}_ECA": [8]},
        {"ORDEN": [1], f"OPF_{NIT}_ECA": [2, 3], f"PDE_{NIT}_ECA": [4, 5, 6, 7], f"CRC_{NIT}_ECA": [8]},
        {"ORDEN": [1], f"OPF_{NIT}_ECA": [2, 3, 4], f"PDE_{NIT}_ECA": [5, 6, 7], f"CRC_{NIT}_ECA": [8]}
    ],
    9: [
        {"ORDEN": [1], f"OPF_{NIT}_ECA": [2, 3, 4], f"PDE_{NIT}_ECA": [5, 6, 7, 8], f"CRC_{NIT}_ECA": [9]},
        {"ORDEN": [1], f"OPF_{NIT}_ECA": [2, 3], f"PDE_{NIT}_ECA": [4, 5, 6, 7, 8], f"CRC_{NIT}_ECA": [9]}
    ],
    10: [
        {"ORDEN": [1], f"OPF_{NIT}_ECA": [2, 3, 4], f"PDE_{NIT}_ECA": [5, 6, 7, 8, 9], f"CRC_{NIT}_ECA": [10]}
    ]
}

def dividir_pdf_por_paginas(pdf_path, carpeta_destino):
    doc = fitz.open(pdf_path)
    paginas = []
    for i in range(len(doc)):
        nueva_ruta = carpeta_destino / f"pagina_{i+1}.pdf"
        nuevo_doc = fitz.open()
        nuevo_doc.insert_pdf(doc, from_page=i, to_page=i)
        nuevo_doc.save(nueva_ruta)
        nuevo_doc.close()
        paginas.append(nueva_ruta)
    doc.close()
    return paginas

def combinar_paginas(paginas, salida):
    nuevo_doc = fitz.open()
    for pagina in paginas:
        doc = fitz.open(pagina)
        nuevo_doc.insert_pdf(doc)
        doc.close()
    nuevo_doc.save(salida)
    nuevo_doc.close()

def procesar_pdfs_en_directorio():
    for archivo in os.listdir():
        if archivo.lower().endswith(".pdf"):
            nombre_base = Path(archivo).stem
            carpeta = Path(nombre_base)
            carpeta.mkdir(exist_ok=True)

            paginas = dividir_pdf_por_paginas(archivo, carpeta)
            total_paginas = len(paginas)

            if total_paginas in combinaciones:
                opciones = combinaciones[total_paginas]
                if total_paginas == 4:
                    etiquetas = ["ORDEN", f"OPF_{NIT}_ECA", f"PDE_{NIT}_ECA", f"CRC_{NIT}_ECA"]
                    for i, etiqueta in enumerate(etiquetas):
                        destino = carpeta / f"{etiqueta}.pdf"
                        paginas[i].rename(destino)
                else:
                    for idx, opcion in enumerate(opciones, start=1):
                        subcarpeta = carpeta / f"opc_{idx}"
                        subcarpeta.mkdir(exist_ok=True)
                        for etiqueta, indices in opcion.items():
                            archivos_a_combinar = [carpeta / f"pagina_{i}.pdf" for i in indices]
                            salida = subcarpeta / f"{etiqueta}.pdf"
                            combinar_paginas(archivos_a_combinar, salida)

if __name__ == "__main__":
    procesar_pdfs_en_directorio()


