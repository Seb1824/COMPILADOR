import re
import subprocess
from pathlib import Path
from src.token import Token, TokenType

_PATRON_GCC = re.compile(
    r'^(?P<archivo>[A-Za-z]:[/\\][^:]+\.c|[^:]+\.c):(?P<linea>\d+):(?P<columna>\d+):\s*(?P<severidad>error|warning|note):\s*(?P<mensaje>.+)$'
)

# lineas de contexto que GCC imprime pero no son mensajes de error:
# "   4 |     printf(...)  " o  "      |         ^~~~~"
_PATRON_CONTEXTO = re.compile(r'^\s*\d+\s*\||\s*\|[\s^~]*$')

# Patrones para extraer el símbolo problemático del mensaje
_PATRONES_SIMBOLO = [
    re.compile(r"'(?P<simbolo>[^']+)'"),        # cualquier cosa entre comillas simples
    re.compile(r'"(?P<simbolo>[^"]+)"'),         # cualquier cosa entre comillas dobles
]

# Patrones para clasificar el tipo de error a partir del mensaje
_PATRONES_TIPO = [
    (re.compile(r'undeclared|not declared|undefined'),          'undeclared'),
    (re.compile(r"expected\s+'?[^']+'?\s+before"),              'expected_token'),
    (re.compile(r'implicit declaration'),                       'implicit_declaration'),
    (re.compile(r'incompatible type|cannot convert'),           'type_mismatch'),
    (re.compile(r'too (few|many) argument'),                    'wrong_arguments'),
    (re.compile(r'unused variable|unused parameter'),           'unused_variable'),
    (re.compile(r'return type|return value'),                   'return_error'),
    (re.compile(r'redeclar|redefinit'),                         'redeclaration'),
    (re.compile(r'divide|division by zero'),                    'division_by_zero'),
]


def _extraer_simbolo(mensaje: str) -> str | None:
    for patron in _PATRONES_SIMBOLO:
        m = patron.search(mensaje)
        if m:
            return m.group('simbolo')
    return None


def _clasificar_tipo(mensaje: str) -> str:
    for patron, tipo in _PATRONES_TIPO:
        if patron.search(mensaje, re.IGNORECASE):
            return tipo
    return 'desconocido'


def _tokenizar_linea(linea: str) -> list[Token]:
    """Convierte una línea del stderr de GCC en una lista de tokens."""
    linea = linea.strip()
    if not linea:
        return []

    # Ignorar líneas de contexto como "4 |  printf(...)" o "  |  ^~~~~"
    if _PATRON_CONTEXTO.match(linea):
        return []

    # Ignorar líneas informativas de GCC
    if re.search(r'In function|In file included', linea):
        return []

    m = _PATRON_GCC.match(linea)
    if not m:
        return [Token(TokenType.DESCONOCIDO, linea)]

    tokens = [
        Token(TokenType.ARCHIVO,       m.group('archivo')),
        Token(TokenType.LINEA,         m.group('linea')),
        Token(TokenType.COLUMNA,       m.group('columna')),
        Token(TokenType.SEVERIDAD,     m.group('severidad')),
        Token(TokenType.MENSAJE_CRUDO, m.group('mensaje')),
        Token(TokenType.TIPO_ERROR,    _clasificar_tipo(m.group('mensaje'))),
    ]

    simbolo = _extraer_simbolo(m.group('mensaje'))
    if simbolo:
        tokens.append(Token(TokenType.SIMBOLO, simbolo))

    return tokens


class Lexer:
    """
    Recibe la ruta a un archivo .c, lo compila con GCC,
    captura el stderr automáticamente y lo tokeniza.
    """

    def __init__(self, ruta_archivo: str):
        self.ruta_archivo = Path(ruta_archivo)
        self.stderr_crudo: str = ""
        self.tokens: list[Token] = []

    def compilar_y_capturar(self) -> str:
        """Ejecuta GCC sobre el archivo y devuelve el stderr completo."""
        resultado = subprocess.run(
            ["gcc", "-Wall", "-o", "/dev/null", str(self.ruta_archivo)],
            capture_output=True,
            text=True
        )
        self.stderr_crudo = resultado.stderr
        return self.stderr_crudo

    def tokenizar(self) -> list[Token]:
        """
        Compila el archivo, captura el stderr y retorna
        la lista de tokens extraídos de todos los mensajes de error.
        """
        if not self.stderr_crudo:
            self.compilar_y_capturar()

        self.tokens = []
        for linea in self.stderr_crudo.splitlines():
            self.tokens.extend(_tokenizar_linea(linea))

        return self.tokens