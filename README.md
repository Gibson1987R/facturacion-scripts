# Scripts de Facturación Médica (RIPS)

Herramientas de línea de comandos en Python para procesar documentación de
facturación en salud (Colombia, formato RIPS). Automatizan tareas manuales y
repetitivas sobre PDFs y archivos JSON de autorizaciones y consultas.

> **Uso interno.** Este repositorio es privado y contiene lógica específica de
> un flujo de facturación concreto. No incluye ni debe incluir datos de
> pacientes, facturas ni JSONs reales.

## ¿Por qué existe?

El flujo de facturación recibía lotes de archivos desordenados:

- PDFs de autorización que llegan **combinados en un solo archivo** y deben
  partirse y recombinarse por tipo de documento (ORDEN, OPF, PDE, CRC, OTR,
  HEV).
- PDFs numerados que deben **unirse en orden** (pág. 1, 2, 3…).
- Facturas escaneadas (sin texto) de las que hay que **extraer datos** para una
  planilla.
- Documentos Word (`.doc`/`.docx`) que deben convertirse a PDF.
- JSONs (RIPS de consultas) que deben **normalizarse** según reglas de
  diagnóstico.

Estos scripts reemplazan minutos de trabajo manual y evitan errores de
ordenamiento o de etiquetado.

## Requisitos

- Python 3.8+
- `pip install PyMuPDF`  (todas las herramientas de PDF)
- `pip install pandas openpyxl` (solo extractor)
- OCR opcional (solo extractor): `pip install pytesseract pillow` y Tesseract
  instalado en `C:\Program Files\Tesseract-OCR\tesseract.exe`
- LibreOffice (`soffice`) en el PATH (solo `doc_pdf.py`)

## Herramientas

| Script | Qué hace |
|---|---|
| `src/combinador.py` | Divide un PDF en páginas y lo recombina en los documentos ORDEN / OPF / PDE / CRC según combinaciones válidas por número total de páginas (4–10). |
| `src/ofta.py` | Variante de oficios: divide y recombina en OTR / CRC / HEV para PDFs de 6+ páginas. |
| `src/unir.py` | Une todos los PDFs de una carpeta en uno solo, ordenados por el número final del nombre (o alfabéticamente con `--alphabetic`). |
| `src/extractor.py` | Extrae campos (FECHA EXP., CONTRATANTE, N.SOPORTE, ID, No. HISTORIA, DIAGNOSTICO, AUTORIZACION, ESPECIALIDAD) de la primera página de cada PDF y exporta un Excel. Usa texto embebido, bloques u OCR en ese orden. |
| `src/doc_pdf.py` | Convierte todos los `.doc`/`.docx` de la carpeta `documentos/` a PDF en `pdfs/` usando LibreOffice headless. |
| `src/actualizador.py` | Ajusta un JSON EJE: para consultas cuyo diagnóstico principal es Z001–Z008, fija `finalidadTecnologiaSalud = "11"` y `causaMotivoAtencion = "40"`. Genera una copia. |
| `src/json_actualizador.py` | Misma lógica de normalización, pero como CLI flexible: acepta un archivo o un directorio completo de JSONs y genera `*_modified.json`. |

## Workflow típico

```
Lote recibido
      │
      ▼
┌─────────────────────┐   ┌──────────────────────┐
│ PDFs combinados     │   │ PDFs numerados       │
│ (autorizaciones)    │   │ (pág 1, 2, 3 …)      │
└──────────┬──────────┘   └──────────┬───────────┘
           │                         │
           ▼                         ▼
   python combinador.py      python unir.py -f carpeta -o unido.pdf
   (o ofta.py para oficios)  (orden por número final)
           │
           ▼
   ┌──────────────────┐   ┌──────────────────────┐
   │ Facturas (PDFs)  │   │ JSON RIPS de        │
   │ para extraer     │   │ consultas           │
   └────────┬─────────┘   └──────────┬───────────┘
            │                        │
            ▼                        ▼
   python extractor.py      python actualizador.py EJE.JSON
   → datos_extraidos.xlsx   → EJE_copia.json
            │
            ▼
   ┌──────────────────────┐
   │ Word → PDF           │
   │ python doc_pdf.py    │
   └──────────────────────┘
```

### Paso a paso

1. **Recombinar autorizaciones** — coloca los PDFs combinados en la carpeta y
   ejecuta `combinador.py` (4–10 páginas) o `ofta.py` (6+ páginas, variante de
   oficios). Cada PDF original genera una carpeta por su nombre con subcarpetas
   `opc_1`, `opc_2`, … (las opciones válidas de combinación). Para PDFs de
   exactamente 4 páginas se usa la única combinación directa.
2. **Unir PDFs numerados** — ejecuta `unir.py -f ruta -o salida.pdf`. Detecta
   el número final de cada nombre para ordenar; con `--alphabetic` ordena por
   nombre. Pregunta antes de sobrescribir.
3. **Extraer datos de facturas** — ejecuta `extractor.py` dentro de la carpeta
   de PDFs. Genera `datos_extraidos.xlsx` y archivos `_debug_*` por PDF para
   auditar el método de lectura (embedded / blocks / ocr / none).
4. **Normalizar JSONs de consultas** — `actualizador.py EJE.JSON` produce
   `EJE_copia.json`; o `json_actualizador.py -i ruta` (archivo o carpeta) para
   procesar muchos a la vez generando `*_modified.json`.
5. **Convertir Word a PDF** — coloca los `.doc`/`.docx` en `documentos/` y
   ejecuta `doc_pdf.py`; los PDFs quedan en `pdfs/`.

## Notas

- `combinador.py` y `ofta.py` procesan los `.pdf` del **directorio actual**
  (no recursivo).
- `extractor.py` también opera sobre los `.pdf` del directorio actual y
  guarda sus salidas ahí mismo.
- Los códigos `842000004` / `_ECA` presentes en los nombres de salida son
  identificadores internos del flujo (prestador/facturación); se mantienen
  como están en los scripts originales.
- **Nunca subir** archivos de datos (`.json` reales, `.pdf`, `.xlsx`, `.exe`)
  a este repositorio: contienen información de pacientes y facturación.

## Estructura

```
facturacion-scripts/
├── README.md
├── .gitignore
└── src/
    ├── combinador.py
    ├── ofta.py
    ├── unir.py
    ├── extractor.py
    ├── doc_pdf.py
    ├── actualizador.py
    └── json_actualizador.py
```