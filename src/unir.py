import os
import re
import glob
import argparse
import fitz  # PyMuPDF

def trailing_number_key(path):
    name = os.path.splitext(os.path.basename(path))[0]
    m = re.search(r'(\d+)$', name)
    if m:
        return (0, int(m.group(1)), name.lower())
    return (1, name.lower())

def find_pdfs(folder):
    return glob.glob(os.path.join(folder, "*.pdf"))

def combine_pdfs(pdf_paths, out_path):
    if not pdf_paths:
        raise ValueError("No se encontraron archivos PDF para combinar.")
    combined = fitz.open()
    paginas = 0
    for p in pdf_paths:
        try:
            with fitz.open(p) as src:
                combined.insert_pdf(src)
                paginas += getattr(src, "page_count", len(src))
                print(f"+ Agregado: {os.path.basename(p)} ({getattr(src,'page_count',len(src))} pág.)")
        except Exception as e:
            print(f"Error al abrir {os.path.basename(p)}: {e}")
    combined.save(out_path)
    combined.close()
    return paginas

def main():
    ap = argparse.ArgumentParser(description="Unir PDFs numerados en una carpeta (orden por número final).")
    ap.add_argument("-f", "--folder", default=".", help="Carpeta con los PDFs (por defecto: actual).")
    ap.add_argument("-o", "--output", default="unido.pdf", help="Nombre del PDF de salida.")
    ap.add_argument("--alphabetic", action="store_true", help="Ordenar alfabéticamente en vez de numérico.")
    args = ap.parse_args()

    folder = os.path.abspath(args.folder)
    if not os.path.isdir(folder):
        print("Carpeta no encontrada:", folder); return

    pdfs = find_pdfs(folder)
    if not pdfs:
        print("No se encontraron PDFs en:", folder); return

    if args.alphabetic:
        pdfs.sort(key=lambda p: os.path.basename(p).lower())
    else:
        pdfs.sort(key=trailing_number_key)

    print("Orden de archivos a unir:")
    for i, p in enumerate(pdfs, 1):
        print(f" {i:02d}. {os.path.basename(p)}")

    out_path = os.path.join(folder, args.output)
    if os.path.exists(out_path):
        ans = input(f"'{out_path}' ya existe. Sobrescribir? [y/N]: ").strip().lower()
        if ans != "y":
            print("Operación cancelada."); return

    try:
        paginas = combine_pdfs(pdfs, out_path)
        print(f"\nPDF combinado guardado: {out_path} ({paginas} páginas).")
    except Exception as e:
        print("Error combinando PDFs:", e)

if __name__ == "__main__":
    main()
