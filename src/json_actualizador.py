import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List

# ------------- Constantes -------------------------------------------------
TARGET_CODES = {
    "Z001", "Z002", "Z003", "Z004", "Z005", "Z006", "Z007", "Z008"
}
CODIGO_CAUSA = "40"
CODIGO_FINALIDAD = "11"


# ------------- Funciones auxiliares ---------------------------------------
def load_json(path: Path) -> Dict[str, Any]:
    """Carga un JSON y devuelve el objeto Python."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(data: Dict[str, Any], path: Path) -> None:
    """Escribe el objeto en formato JSON con indentación 2."""
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def procesar_consulta(consulta: Dict[str, Any]) -> None:
    """
    Modifica la consulta en‑place si el diagnostico principal está en TARGET_CODES.
    """
    cod = consulta.get("codDiagnosticoPrincipal")
    if cod in TARGET_CODES:
        consulta["causaMotivoAtencion"] = CODIGO_CAUSA
        consulta["finalidadTecnologiaSalud"] = CODIGO_FINALIDAD


def procesar_usuario(usuario: Dict[str, Any]) -> None:
    """
    Recorre servicios > consultas y aplica procesar_consulta.
    """
    servicios = usuario.get("servicios", [])
    for servicio in servicios:
        consultas = servicio.get("consultas", [])
        for consulta in consultas:
            procesar_consulta(consulta)


def procesar_archivo(original: Path, copia: Path) -> None:
    """
    Carga, modifica y guarda una copia del JSON.
    """
    data = load_json(original)

    usuarios = data.get("usuarios", [])
    for usuario in usuarios:
        procesar_usuario(usuario)

    dump_json(data, copia)
    print(f"Guardado: {copia}")


# ------------- CLI --------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Actualiza consultas con diagnostico principal en Z001‑Z008."
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Archivo .json o directorio que contiene archivos .json",
    )
    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_file() and input_path.suffix.lower() == ".json":
        # Solo un archivo
        copia = input_path.with_name(
            f"{input_path.stem}_modified.json"
        )
        procesar_archivo(input_path, copia)

    elif input_path.is_dir():
        # Procesa todos los .json dentro del directorio (no recursivo)
        for json_file in input_path.glob("*.json"):
            copia = json_file.with_name(
                f"{json_file.stem}_modified.json"
            )
            procesar_archivo(json_file, copia)

    else:
        print("Error: la ruta indicada no es un archivo JSON ni un directorio.")
        exit(1)


if __name__ == "__main__":
    main()