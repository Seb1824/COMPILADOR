from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from src.token import Token, TokenType

@dataclass
class DiagnosticEntry:
    archivo: str
    linea: int
    columna: int
    severidad: str
    mensaje_crudo: str
    tipo_error: str
    simbolo: Optional[str] = None


class Parser:
    """Agrupa tokens del lexer en diagnósticos estructurados."""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens

    def parse(self) -> list[DiagnosticEntry]:
        diagnosticos: list[DiagnosticEntry] = []
        i = 0

        while i < len(self.tokens):
            token = self.tokens[i]

            if token.tipo != TokenType.ARCHIVO:
                i += 1
                continue

            resultado = self._parse_diagnostic(i)
            if resultado is None:
                i += 1
                continue

            diagnostico, siguiente_indice = resultado
            diagnosticos.append(diagnostico)
            i = siguiente_indice

        return diagnosticos

    def _parse_diagnostic(self, start_index: int) -> tuple[DiagnosticEntry, int] | None:
        """
        ARCHIVO LINEA COLUMNA SEVERIDAD MENSAJE_CRUDO TIPO_ERROR [SIMBOLO]
        """
        required = [
            TokenType.ARCHIVO,
            TokenType.LINEA,
            TokenType.COLUMNA,
            TokenType.SEVERIDAD,
            TokenType.MENSAJE_CRUDO,
            TokenType.TIPO_ERROR,
        ]

        if start_index + len(required) > len(self.tokens):
            return None

        chunk = self.tokens[start_index:start_index + len(required)]

        for expected, current in zip(required, chunk):
            if current.tipo != expected:
                return None

        archivo = chunk[0].valor

        try:
            linea = int(chunk[1].valor)
            columna = int(chunk[2].valor)
        except ValueError:
            return None

        severidad = chunk[3].valor
        mensaje_crudo = chunk[4].valor
        tipo_error = chunk[5].valor

        next_index = start_index + len(required)
        simbolo = None

        if next_index < len(self.tokens) and self.tokens[next_index].tipo == TokenType.SIMBOLO:
            simbolo = self.tokens[next_index].valor
            next_index += 1

        return (
            DiagnosticEntry(
                archivo=archivo,
                linea=linea,
                columna=columna,
                severidad=severidad,
                mensaje_crudo=mensaje_crudo,
                tipo_error=tipo_error,
                simbolo=simbolo,
            ),
            next_index,
        )