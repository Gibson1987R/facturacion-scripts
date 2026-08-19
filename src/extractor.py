# ...existing code...
import os
import re
import io
import traceback
import fitz  # PyMuPDF
import pandas as pd

# OCR opcional
try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    OCR_AVAILABLE = True
except Exception:
    pytesseract = None
    Image = None
    ImageEnhance = None
    ImageFilter = None
    OCR_AVAILABLE = False

# Si usas Windows y Tesseract no está en PATH, ajusta aquí la ruta
TESSERACT_CMD = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if OCR_AVAILABLE:
    try:
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    except Exception:
        pass

# Patrones para extraer datos (case-insensitive)
PATRONES = {
    "FECHA EXP.": r"FECHA\s*EXP\.?:?\s*([A-Za-z0-9./:\s\-]+)",
    "CONTRATANTE": r"CONTRATANTE\s*[:]*\s*([A-ZÁÉÍÓÚÑ0-9\-\.\s]+)",
    "N.SOPORTE": r"N\.?SOPORTE\s*[:]*\s*([0-9\s\-]+)",
    "ID": r"\bID\s*[:]*\s*(CC|PT)\s*([0-9\.\-]+)",
    "No. HISTORIA": r"No\.?\s*HISTORIA\s*[:]*\s*([0-9]+)",
    "DIAGNOSTICO": r"DIAGNOSTICO\s*[:]*\s*([A-Z0-9\-\.]+)",
    "AUTORIZACION": r"AUTORIZA(?:CION|CIÓN)\s*[:\s]*([0-9\-]+)",
    "ESPECIALIDAD": r"ESPECIALIDAD\s*[:]*\s*([A-ZÁÉÍÓÚÑ0-9\s\/\-\.\,]+)"
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def preprocesar_imagen(img, min_dim=1000, contrast=1.8):
    """Mejora la imagen para OCR: escala de grises, redimensiona, aumenta contraste y afila."""
    if Image is None or img is None:
        return img
    img = img.convert("L")
    w, h = img.size
    if max(w, h) < min_dim:
        factor = (min_dim // max(w, h)) + 1
        img = img.resize((int(w*factor), int(h*factor)), Image.LANCZOS)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = img.filter(ImageFilter.SHARPEN)
    return img

def extraer_texto(pdf_path, ocr_dpi=300, ocr_config="--psm 6 --oem 3"):
    """Extrae texto de la primera página.
    Devuelve (texto, ruta_imagen_ocr, metodo) con metodo en {'embedded','blocks','ocr','none'}."""
    metodo = "none"
    ocr_image_path = ""
    texto = ""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise RuntimeError(f"Error abriendo PDF '{pdf_path}': {e}")
    try:
        page = doc.load_page(0)
        # intento 1: texto plano
        texto = page.get_text("text") or ""
        if texto.strip():
            metodo = "embedded"
        else:
            # intento 2: bloques (algunas PDFs tienen texto en blocks)
            blocks = page.get_text("blocks") or []
            if blocks:
                texto = " ".join(str(b[4]) for b in blocks if b and len(b) > 4).strip()
                if texto:
                    metodo = "blocks"
        # intento 3: OCR si no hay texto y OCR disponible
        if not texto.strip() and OCR_AVAILABLE:
            pix = page.get_pixmap(dpi=ocr_dpi, alpha=False)
            png_bytes = pix.tobytes("png")
            try:
                img = Image.open(io.BytesIO(png_bytes))
                img = preprocesar_imagen(img)
                # ejecutar OCR
                try:
                    ocr_text = pytesseract.image_to_string(img, lang="spa", config=ocr_config) or ""
                    texto = ocr_text.strip()
                    if texto:
                        metodo = "ocr"
                except Exception:
                    texto = ""
                # guardar imagen debug
                try:
                    ocr_image_path = os.path.join(BASE_DIR, f"_debug_{os.path.splitext(os.path.basename(pdf_path))[0]}_p1.png")
                    img.save(ocr_image_path)
                except Exception:
                    ocr_image_path = ""
            except Exception:
                texto = texto or ""
        return texto or "", ocr_image_path, metodo
    finally:
        doc.close()

def extraer_valores(texto):
    """Extrae valores usando PATRONES. Normaliza espacios antes de buscar."""
    texto_norm = re.sub(r"\s+", " ", (texto or "")).strip()
    datos = {}
    for clave, patron in PATRONES.items():
        if clave == "ID":
            m = re.search(patron, texto_norm, re.IGNORECASE)
            if m:
                datos[clave] = f"{m.group(1).upper()} {m.group(2)}"
            else:
                datos[clave] = ""
        else:
            m = re.search(patron, texto_norm, re.IGNORECASE)
            datos[clave] = m.group(1).strip() if m else ""
    return datos

def main():
    resultados = []
    pdf_files = [f for f in os.listdir(BASE_DIR) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print(f"No se encontraron PDFs en: {BASE_DIR}")
        return

    print(f"OCR disponible: {OCR_AVAILABLE}")
    for archivo in sorted(pdf_files):
        ruta = os.path.join(BASE_DIR, archivo)
        print(f"\nProcesando: {archivo}")
        try:
            texto, ocr_img, metodo = extraer_texto(ruta)
        except Exception as e:
            print(f"  Error leyendo PDF: {e}")
            resultados.append({"Archivo": archivo, **{k: "" for k in PATRONES.keys()}})
            continue

        # guardar debug del texto con método
        debug_txt = os.path.join(BASE_DIR, f"_debug_{os.path.splitext(archivo)[0]}_p1.txt")
        try:
            with open(debug_txt, "w", encoding="utf-8") as f:
                f.write(f"METODO: {metodo}\n\n")
                f.write(texto or "<NO_TEXT>")
            print(f"  Debug guardado: {debug_txt} (método: {metodo})")
            if ocr_img:
                print(f"  Imagen OCR guardada: {ocr_img}")
        except Exception as e:
            print(f"  No se pudo guardar debug: {e}")

        datos = extraer_valores(texto)
        datos["Archivo"] = archivo
        datos["_METODO_LECTURA"] = metodo
        resultados.append(datos)

        # mostrar hallazgos
        for k in list(PATRONES.keys()):
            v = datos.get(k, "")
            print(f"   {k}: {v if v else '[NO ENCONTRADO]'}")

    # exportar Excel
    if resultados:
        cols = list(PATRONES.keys()) + ["Archivo", "_METODO_LECTURA"]
        df = pd.DataFrame(resultados)
        df = df[cols]
        excel_path = os.path.join(BASE_DIR, "datos_extraidos.xlsx")
        try:
            df.to_excel(excel_path, index=False)
            print(f"\nGuardado: {excel_path}")
        except Exception as e:
            errfile = os.path.join(BASE_DIR, "_error_extractor.txt")
            with open(errfile, "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())
            print(f"Error guardando Excel. Revisa: {errfile}")

if __name__ == "__main__":
    main()
# ...existing code...
