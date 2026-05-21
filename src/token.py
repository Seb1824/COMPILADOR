from enum import Enum
from dataclasses import dataclass


class TokenType(Enum):
    ARCHIVO         = "ARCHIVO"          # nombre del archivo fuennte
    LINEA           = "LINEA"            # número de línea donde ocurrió el error
    COLUMNA         = "COLUMNA"          # número de columna
    SEVERIDAD       = "SEVERIDAD"        # "error" o "warning"
    TIPO_ERROR      = "TIPO_ERROR"       # ej: undeclared, expected, implicit, etc.
    SIMBOLO         = "SIMBOLO"          # identificador o símbolo problemático, ej: 'x', ';'
    MENSAJE_CRUDO   = "MENSAJE_CRUDO"    # texto completo del error sin procesar
    DESCONOCIDO     = "DESCONOCIDO"      # cualquier parte que no encaje con los patrones


@dataclass
class Token:
    tipo: TokenType
    valor: str

    def __repr__(self):
        return f"Token({self.tipo.value}, {self.valor!r})"