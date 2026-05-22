import argparse
from pathlib import Path

from src.lexer import Lexer
from src.parser import Parser


def run_pipeline(ruta_archivo: str) -> int:
    ruta = Path(ruta_archivo)
    if not ruta.exists():
        print(f"[ERROR] No existe el archivo: {ruta}")
        return 1

    lexer = Lexer(str(ruta))
    stderr = lexer.compilar_y_capturar()
    tokens = lexer.tokenizar()
    diagnosticos = Parser(tokens).parse()

    print("=== STDERR CRUDO (GCC) ===")
    print(stderr.strip() or "(sin salida)")

    print("\n=== TOKENS ===")
    if not tokens:
        print("(sin tokens)")
    else:
        for t in tokens:
            print(t)

    print("\n=== DIAGNOSTICOS (PARSER) ===")
    if not diagnosticos:
        print("(sin diagnósticos)")
    else:
        for i, d in enumerate(diagnosticos, start=1):
            print(f"[{i}] archivo={d.archivo} linea={d.linea} columna={d.columna}")
            print(f"    severidad={d.severidad} tipo_error={d.tipo_error} simbolo={d.simbolo}")
            print(f"    mensaje={d.mensaje_crudo}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Pipeline Lexer -> Parser para diagnósticos de GCC")
    parser.add_argument("archivo", help="Ruta al archivo .c a compilar")
    args = parser.parse_args()

    return run_pipeline(args.archivo)


if __name__ == "__main__":
    raise SystemExit(main())