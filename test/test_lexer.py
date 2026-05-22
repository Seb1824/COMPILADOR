import os
from src.lexer import Lexer
from src.token import TokenType

RUTA_CORRECTO   = os.path.join(os.path.dirname(__file__), '..', 'examples', 'correcto.c')
RUTA_ERROR      = os.path.join(os.path.dirname(__file__), '..', 'examples', 'error_lexico.c')


def test_archivo_correcto_no_genera_tokens():
    """Un archivo sin errores no debe producir ningún token de error."""
    lexer = Lexer(RUTA_CORRECTO)
    tokens = lexer.tokenizar()
    errores = [t for t in tokens if t.tipo == TokenType.SEVERIDAD and t.valor == 'error']
    assert len(errores) == 0, f"Se esperaban 0 errores, se encontraron: {errores}"
    print("PASS: archivo correcto no genera tokens de error")


def test_archivo_con_error_genera_tokens():
    """Un archivo con errores debe producir al menos un token de cada tipo básico."""
    lexer = Lexer(RUTA_ERROR)
    tokens = lexer.tokenizar()

    tipos_presentes = {t.tipo for t in tokens}

    assert TokenType.ARCHIVO in tipos_presentes,    "Falta token ARCHIVO"
    assert TokenType.LINEA in tipos_presentes,      "Falta token LINEA"
    assert TokenType.SEVERIDAD in tipos_presentes,  "Falta token SEVERIDAD"
    assert TokenType.MENSAJE_CRUDO in tipos_presentes, "Falta token MENSAJE_CRUDO"
    assert TokenType.TIPO_ERROR in tipos_presentes, "Falta token TIPO_ERROR"
    print("PASS: archivo con error genera todos los tipos de token esperados")


def test_stderr_se_captura_automaticamente():
    """El lexer debe capturar stderr sin intervención del usuario."""
    lexer = Lexer(RUTA_ERROR)
    lexer.compilar_y_capturar()
    assert len(lexer.stderr_crudo) > 0, "stderr vacío — no se capturó nada"
    print("PASS: stderr capturado automáticamente")


def test_tokens_tienen_valores_no_vacios():
    """Ningún token debe tener un valor vacío."""
    lexer = Lexer(RUTA_ERROR)
    tokens = lexer.tokenizar()
    vacios = [t for t in tokens if not t.valor.strip()]
    assert len(vacios) == 0, f"Tokens con valor vacío: {vacios}"
    print("PASS: todos los tokens tienen valores no vacíos")


if __name__ == "__main__":
    test_stderr_se_captura_automaticamente()
    test_archivo_correcto_no_genera_tokens()
    test_archivo_con_error_genera_tokens()
    test_tokens_tienen_valores_no_vacios()
    
    print("\nTodos los tests pasaron.")

def test_lexer_retorna_desconocido_para_linea_no_parseable():
    from src.lexer import _tokenizar_linea

    tokens = _tokenizar_linea("linea inventada sin formato gcc")
    assert len(tokens) == 1
    assert tokens[0].tipo == TokenType.DESCONOCIDO