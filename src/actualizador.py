import argparse
from pathlib import Path
import sys

# Cargar explícitamente json del stdlib para evitar conflicto con archivos locales json.py
# Hace un import temporal tras quitar ruta actual de sys.path.
def _import_json_stdlib():
    current_dir = Path.cwd().resolve()
    script_dir = Path(__file__).resolve().parent
    removed = []

    for p in list(sys.path):
        if p and Path(p).resolve() in {current_dir, script_dir}:
            removed.append((p, sys.path.index(p)))
            sys.path.remove(p)

    try:
        import json as std_json
    except Exception as e:
        raise ImportError('No se pudo importar json estándar.') from e
    finally:
        for p, idx in reversed(removed):
            sys.path.insert(idx, p)

    return std_json

try:
    import json
    if not hasattr(json, 'load'):
        raise ImportError
except Exception:
    json = _import_json_stdlib()

FLAG_CODES = {'Z001','Z002','Z003','Z004','Z005','Z006','Z007','Z008'}

def procesar_json(input_path: Path, output_path: Path):
    with input_path.open('r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("El JSON debe ser un objeto raíz (dict).")

    usuarios = data.get('usuarios', [])
    if not isinstance(usuarios, list):
        raise ValueError("El campo 'usuarios' debe ser una lista.")

    cambios = 0
    for user in usuarios:
        servicios = user.get('servicios', {})
        if not isinstance(servicios, dict):
            continue

        consultas = servicios.get('consultas', [])
        if not isinstance(consultas, list):
            continue

        for consulta in consultas:
            if not isinstance(consulta, dict):
                continue

            cdp = consulta.get('codDiagnosticoPrincipal')
            if isinstance(cdp, str) and cdp.strip() in FLAG_CODES:
                if consulta.get('finalidadTecnologiaSalud') != '11':
                    consulta['finalidadTecnologiaSalud'] = '11'
                    cambios += 1
                if consulta.get('causaMotivoAtencion') != '40':
                    consulta['causaMotivoAtencion'] = '40'
                    cambios += 1

    with output_path.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return cambios

def main():
    parser = argparse.ArgumentParser(description="Transforma EJE JSON con reglas de diagnóstico.")
    parser.add_argument("input", nargs='?', default='EJE.JSON', help="Archivo JSON origen (p.ej. EJE.JSON)")
    parser.add_argument("--output", "-o", default=None, help="Archivo JSON destino (p.ej. EJE_copia.json)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        alt = Path.cwd().parent / input_path.name
        if alt.exists():
            input_path = alt
            print(f"Archivo origen encontrado en carpeta padre: {input_path}")
        else:
            raise SystemExit(f"No existe {input_path} ni {alt}")

    output_path = Path(args.output) if args.output else input_path.with_name(input_path.stem + "_copia" + input_path.suffix)

    cambios = procesar_json(input_path, output_path)
    print(f"Archivo generado: {output_path}")
    print(f"Campos modificados: {cambios}")

if __name__ == "__main__":
    main()