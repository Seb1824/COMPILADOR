# COMPILADOR

Proyecto de compiladores orientado a construir un pipeline inicial de analisis de errores para programas en C.  
Hasta el momento, el sistema toma un archivo `.c`, lo compila con GCC en modo de revision sintactica, captura la salida de error (`stderr`), la tokeniza y luego la transforma en diagnosticos estructurados.

## Estado actual del proyecto

El avance implementado cubre las primeras etapas del pipeline:

1. Ejecucion de GCC sobre un archivo fuente en C.
2. Captura automatica del `stderr` generado por GCC.
3. Analisis lexico de los mensajes de error y advertencia.
4. Generacion de tokens con informacion relevante del diagnostico.
5. Analisis sintactico de los tokens para formar objetos de diagnostico.
6. Pruebas unitarias para lexer y parser.
7. Ejemplos de entrada correctos y con errores.

Actualmente el proyecto no compila un lenguaje propio completo; por ahora trabaja sobre la salida de GCC para interpretar y estructurar errores de archivos C.

## Estructura del proyecto

```text
COMPILADOR/
├── main.py
├── README.md
├── examples/
│   ├── correcto.c
│   └── error_lexico.c
├── src/
│   ├── __init__.py
│   ├── lexer.py
│   ├── parser.py
│   └── token.py
└── test/
    ├── test_lexer.py
    └── test_parser.py
```

## Componentes implementados

### `main.py`

Contiene el punto de entrada del proyecto. Recibe por consola la ruta de un archivo `.c` y ejecuta el pipeline completo:

```text
archivo .c -> GCC -> stderr -> Lexer -> tokens -> Parser -> diagnosticos
```

La salida muestra:

- El `stderr` crudo generado por GCC.
- La lista de tokens encontrados.
- Los diagnosticos estructurados generados por el parser.

### `src/token.py`

Define los tipos de token usados por el lexer:

- `ARCHIVO`: nombre o ruta del archivo fuente.
- `LINEA`: linea donde GCC detecto el problema.
- `COLUMNA`: columna del problema.
- `SEVERIDAD`: tipo de mensaje (`error`, `warning` o `note`).
- `MENSAJE_CRUDO`: mensaje original emitido por GCC.
- `TIPO_ERROR`: clasificacion interna del error.
- `SIMBOLO`: simbolo o identificador asociado al error, cuando se puede extraer.
- `DESCONOCIDO`: linea que no coincide con los patrones esperados.

Tambien define la clase `Token`, que almacena el tipo y valor de cada token.

### `src/lexer.py`

Implementa el analizador lexico del proyecto.

Responsabilidades principales:

- Ejecutar GCC con:

```bash
gcc -Wall -fsyntax-only archivo.c
```

- Capturar automaticamente el `stderr`.
- Ignorar lineas de contexto de GCC, por ejemplo las lineas con `|`, `^` o `~`.
- Reconocer mensajes con formato:

```text
archivo.c:linea:columna: severidad: mensaje
```

- Generar tokens para archivo, linea, columna, severidad, mensaje, tipo de error y simbolo.
- Clasificar errores comunes.

Tipos de error reconocidos actualmente:

- `undeclared`
- `expected_token`
- `implicit_declaration`
- `type_mismatch`
- `wrong_arguments`
- `unused_variable`
- `return_error`
- `redeclaration`
- `division_by_zero`
- `desconocido`

### `src/parser.py`

Implementa el parser que agrupa tokens consecutivos en diagnosticos.

El parser espera secuencias con esta forma:

```text
ARCHIVO LINEA COLUMNA SEVERIDAD MENSAJE_CRUDO TIPO_ERROR [SIMBOLO]
```

Cuando encuentra una secuencia valida, construye un `DiagnosticEntry` con:

- `archivo`
- `linea`
- `columna`
- `severidad`
- `mensaje_crudo`
- `tipo_error`
- `simbolo`

Tambien ignora tokens sueltos, bloques incompletos y diagnosticos con linea o columna no numericas.

## Ejemplos incluidos

### `examples/correcto.c`

Archivo C valido. Sirve para comprobar que un programa sin errores no produce tokens de error.

### `examples/error_lexico.c`

Archivo C con errores intencionales. Sirve para probar la captura de errores, tokenizacion y generacion de diagnosticos.

Errores incluidos:

- Uso de variable no declarada (`y`).
- Falta de punto y coma despues de una asignacion.
- Asignacion incompatible de cadena a entero.

## Uso

Requisitos:

- Python 3.10 o superior.
- GCC instalado y disponible en el `PATH`.

Ejecutar el pipeline sobre el ejemplo con errores:

```bash
python main.py examples/error_lexico.c
```

Ejecutar el pipeline sobre el ejemplo correcto:

```bash
python main.py examples/correcto.c
```

En Windows, si `python` no esta disponible pero existe el lanzador `py`, se puede usar:

```bash
py main.py examples/error_lexico.c
```

## Pruebas

El proyecto incluye pruebas para el lexer y el parser.

Para ejecutarlas:

```bash
python -m pytest -q
```

Pruebas del lexer:

- Verifica que un archivo correcto no genere errores.
- Verifica que un archivo con errores genere tokens basicos.
- Verifica que el `stderr` se capture automaticamente.
- Verifica que los tokens tengan valores no vacios.
- Verifica que una linea no parseable genere un token `DESCONOCIDO`.

Pruebas del parser:

- Verifica que el parser genere diagnosticos desde los tokens del lexer.
- Verifica diagnosticos sin simbolo.
- Verifica que se ignoren bloques incompletos.
- Verifica multiples diagnosticos.
- Verifica que se ignoren tokens desconocidos entre diagnosticos.
- Verifica que se descarten diagnosticos con linea o columna no numericas.

## Verificacion realizada

Desde este entorno se comprobo que GCC esta instalado:

```text
gcc.exe (GCC) 13.2.0
```

No se pudieron ejecutar las pruebas desde el sandbox porque no hay una instalacion de Python disponible mediante `python` ni `py`.

## Pendientes y posibles mejoras

- Instalar o configurar Python en el entorno para ejecutar las pruebas.
- Agregar un archivo `requirements.txt` si se decide formalizar `pytest` como dependencia.
- Mejorar la clasificacion de errores con mas patrones de GCC.
- Agregar soporte para diferentes formatos de rutas y mensajes de compilador.
- Guardar resultados en un archivo de salida, por ejemplo `resultados.txt`.
- Agregar una etapa semantica propia si el proyecto evoluciona hacia un compilador completo.
- Definir una gramatica formal si se implementara un lenguaje propio.

## Resumen

El proyecto ya cuenta con una base funcional para analizar errores de compilacion de C usando GCC. La parte avanzada hasta ahora corresponde a la automatizacion de la captura de errores, su tokenizacion y su transformacion en diagnosticos estructurados mediante un parser simple.
