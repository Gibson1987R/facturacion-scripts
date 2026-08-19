import os
import fitz  # PyMuPDF
from pathlib import Path

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

            if total_paginas >= 6:
                # Opción 1
                opc1 = carpeta / "opc_1"
                opc1.mkdir(exist_ok=True)
                combinar_paginas(paginas[0:4], opc1 / "OTR_842000004_ECA.pdf")
                combinar_paginas([paginas[4]], opc1 / "CRC_842000004_ECA.pdf")
                combinar_paginas(paginas[5:], opc1 / "HEV_842000004_ECA.pdf")

                # Opción 2
                opc2 = carpeta / "opc_2"
                opc2.mkdir(exist_ok=True)
                combinar_paginas(paginas[0:5], opc2 / "OTR_842000004_ECA.pdf")
                combinar_paginas([paginas[5]], opc2 / "CRC_842000004_ECA.pdf")
                combinar_paginas(paginas[6:], opc2 / "HEV_842000004_ECA.pdf")

if __name__ == "__main__":
    procesar_pdfs_en_directorio()
