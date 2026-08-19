# Facturación Hospital — Clasificador de Autorizaciones (RIPS)

Herramienta de línea de comandos en Python que **divide, clasifica y renombra**
los PDFs de autorizaciones de salud (Colombia, formato RIPS) que llegan al
hospital **combinados en un solo archivo**.

> **Proyecto real.** Nace de un problema concreto del flujo de facturación: los
> PDFs de autorización llegaban con varios documentos mezclados en un solo
> archivo (Orden, OPF, PDE, CRC) y había que separarlos a mano, página por
> página. Este script automatiza esa tarea.

> **Uso interno.** Repositorio privado. No incluye ni debe incluir datos de
> pacientes, facturas ni JSONs reales.

## El problema que resuelve

En el hospital, las autorizaciones llegan como un **único PDF combinado** que
contiene hasta 4 tipos de documentos:

| Documento | Contenido |
|---|---|
| **ORDEN** | Orden médica / de compra |
| **OPF** | Orden de prestación de servicios |
| **PDE** | Petición de datos de facturación |
| **CRC** | Certificado / comprobante |

Dependiendo del número total de páginas del PDF, las páginas se reparten entre
esos documentos de una o más maneras posibles. El personal debía abrir cada
PDF, anotar las páginas y reconstruir los documentos a mano, con riesgo de
equivocarse de orden o de mezclar autorizaciones.

## Qué hace `combinador.py`

1. Toma **todos los `.pdf` de la carpeta actual** (uno por autorización).
2. Divide cada PDF en páginas individuales.
3. Según el **número total de páginas (4 a 10)**, prueba las **combinaciones
   válidas** de reparto entre ORDEN / OPF / PDE / CRC.
4. Para cada combinación válida crea una subcarpeta `opc_N` con los
   documentos reconstruidos y **renombrados**:
   `ORDEN.pdf`, `OPF_842000004_ECA.pdf`, `PDE_842000004_ECA.pdf`,
   `CRC_842000004_ECA.pdf`.
5. Deja la carpeta `opc_N` correcta lista para revisar y usar.

Los PDFs de exactamente **4 páginas** usan la única combinación directa
(1 página por documento) y se renombran sin subcarpetas.

### Combinaciones por número de páginas

```
4 pág → ORDEN:1 | OPF:2 | PDE:3 | CRC:4                      (única, directa)
5 pág → opc_1: ORDEN:1 | OPF:2 | PDE:3-4 | CRC:5
        opc_2: ORDEN:1 | OPF:2-3 | PDE:4 | CRC:5
6 pág → opc_1: ORDEN:1 | OPF:2 | PDE:3-5 | CRC:6
        opc_2: ORDEN:1 | OPF:2-3 | PDE:4-5 | CRC:6
        opc_3: ORDEN:1 | OPF:2-4 | PDE:5 | CRC:6
7 pág → opc_1: ORDEN:1 | OPF:2 | PDE:3-6 | CRC:7
        opc_2: ORDEN:1 | OPF:2-3 | PDE:4-6 | CRC:7
        opc_3: ORDEN:1 | OPF:2-4 | PDE:5-6 | CRC:7
8 pág → opc_1: ORDEN:1 | OPF:2 | PDE:3-7 | CRC:8
        opc_2: ORDEN:1 | OPF:2-3 | PDE:4-7 | CRC:8
        opc_3: ORDEN:1 | OPF:2-4 | PDE:5-7 | CRC:8
9 pág → opc_1: ORDEN:1 | OPF:2-4 | PDE:5-8 | CRC:9
        opc_2: ORDEN:1 | OPF:2-3 | PDE:4-8 | CRC:9
10 pág → opc_1: ORDEN:1 | OPF:2-4 | PDE:5-9 | CRC:10
```

## Uso

1. **Copia `combinador.py` en la carpeta** donde están los PDFs a arreglar
   (o ejecútalo desde ahí).
2. Asegúrate de que solo estén los PDFs de autorización a procesar.
3. Ejecuta:

   ```bash
   python combinador.py
   ```

4. Revisa los resultados: cada PDF original ahora es una carpeta con su
   nombre, que contiene las opciones `opc_1`, `opc_2`, … con los documentos
   ORDEN / OPF / PDE / CRC ya separados y renombrados.

### Salida esperada

```
autorizacion_2025-11-03.pdf        ← PDF original combinado
└── autorizacion_2025-11-03/        ← carpeta generada
    ├── opc_1/
    │   ├── ORDEN.pdf
    │   ├── OPF_842000004_ECA.pdf
    │   ├── PDE_842000004_ECA.pdf
    │   └── CRC_842000004_ECA.pdf
    ├── opc_2/
    │   └── … (si hay más de una combinación válida)
```

## Requisitos

- Python 3.8+
- `pip install PyMuPDF`

## Notas

- Procesa los `.pdf` del **directorio actual** (no recursivo).
- El identificador `842000004` / `_ECA` en los nombres de salida es el código
  del prestador del flujo; está integrado en el script porque es parte del
  estándar interno de archivo.
- Para PDFs de más de 10 páginas no hay combinación definida: el script los
  divide en páginas pero no genera opciones.
- **Nunca subir** archivos de datos (`.pdf`, `.xlsx`, `.json`) a este
  repositorio: contienen información de pacientes y facturación.

## Estructura

```
facturacion-scripts/
├── README.md
├── .gitignore
└── src/
    └── combinador.py
```