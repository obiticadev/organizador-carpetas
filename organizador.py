"""Organiza recursivamente archivos en subcarpetas según su extensión.

Conserva los archivos con nombres repetidos mediante sufijos numéricos
y muestra el resumen y el historial de movimientos con Rich.
"""

import os
import shutil

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table


def obtener_extension(nombre_archivo):
    """Obtiene la extensión de un archivo.

    Recibe el nombre del archivo como cadena.
    Devuelve la extensión en minúsculas y sin punto,
    o "sin_extension" si no tiene extensión.
    """
    nombre, extension = os.path.splitext(nombre_archivo)

    if extension == "":
        return "sin_extension"
    return extension[1:].lower()


def tamano_legible(tamano_bytes):
    """Convierte un tamaño en bytes a una unidad legible.

    Recibe un tamaño no negativo en bytes.
    Devuelve una cadena con dos decimales en bytes, KB, MB o GB.
    """
    unidades = ["bytes", "KB", "MB", "GB"]
    tamano = tamano_bytes
    indice = 0

    while tamano >= 1024 and indice < len(unidades) - 1:
        tamano = tamano / 1024
        indice = indice + 1

    return f"{tamano:.2f} {unidades[indice]}"


def una_dentro_de_otra(ruta_a, ruta_b):
    """Comprueba si dos rutas son iguales o una está dentro de la otra.

    Recibe dos rutas como cadenas.
    Devuelve True si son iguales o están anidadas, y False en otro caso.
    """
    absoluta_a = os.path.join(os.path.abspath(ruta_a), "")
    absoluta_b = os.path.join(os.path.abspath(ruta_b), "")

    a_dentro_de_b = absoluta_a.startswith(absoluta_b)
    b_dentro_de_a = absoluta_b.startswith(absoluta_a)

    return a_dentro_de_b or b_dentro_de_a


def nombre_disponible(ruta_destino, nombre_archivo):
    """Busca un nombre libre en la carpeta de destino.

    Recibe la ruta de la carpeta y el nombre original del archivo.
    Devuelve el nombre original si está libre o uno con sufijo numérico.
    """
    nombre, extension = os.path.splitext(nombre_archivo)
    candidato = nombre_archivo
    contador = 1

    while os.path.exists(os.path.join(ruta_destino, candidato)):
        candidato = f"{nombre}_{contador}{extension}"
        contador = contador + 1

    return candidato


def clasificar_archivo(ruta_origen, nombre_archivo, ruta_destino, historial):
    """Mueve un archivo a la subcarpeta correspondiente a su extensión.

    Recibe la ruta completa del archivo, su nombre, la carpeta de destino
    y una lista compartida donde registrar los movimientos.
    Devuelve el tamaño en bytes y añade el movimiento al historial.
    """
    extension = obtener_extension(nombre_archivo)
    carpeta_extension = os.path.join(ruta_destino, extension)

    # Crear la subcarpeta de clasificación.
    os.makedirs(carpeta_extension, exist_ok=True)

    # Elegir un nombre que no sobrescriba archivos existentes.
    nombre_final = nombre_disponible(carpeta_extension, nombre_archivo)
    destino_final = os.path.join(carpeta_extension, nombre_final)

    # Obtener el tamaño antes de mover el archivo.
    tamano = os.path.getsize(ruta_origen)
    shutil.move(ruta_origen, destino_final)

    # Modificar la lista original recibida como parámetro.
    historial.append(f"{ruta_origen} → {destino_final}")

    return tamano


def clasificar_carpeta_recursivo(ruta_origen, ruta_destino, historial):
    """Clasifica los archivos de una carpeta y sus subcarpetas.

    Recibe las carpetas de origen y destino y la lista compartida
    de movimientos.
    Devuelve el total de bytes movidos.
    """
    total_bytes = 0

    # Caso base: si la carpeta está vacía, el bucle no se ejecuta
    # y se devuelve 0. Los archivos se procesan sin más recursión.
    for nombre in os.listdir(ruta_origen):
        ruta_elemento = os.path.join(ruta_origen, nombre)

        if os.path.isdir(ruta_elemento):
            # Caso recursivo: resolver el mismo problema en una subcarpeta.
            bytes_movidos = clasificar_carpeta_recursivo(
                ruta_elemento,
                ruta_destino,
                historial,
            )
            total_bytes = total_bytes + bytes_movidos

        elif os.path.isfile(ruta_elemento):
            bytes_movidos = clasificar_archivo(
                ruta_elemento,
                nombre,
                ruta_destino,
                historial,
            )
            total_bytes = total_bytes + bytes_movidos

    return total_bytes


def contar_archivos_recursivo(ruta):
    """Cuenta los archivos de una carpeta y sus subcarpetas.

    Recibe la ruta de una carpeta existente.
    Devuelve el número total de archivos encontrados.
    """
    total_archivos = 0

    for nombre in os.listdir(ruta):
        ruta_elemento = os.path.join(ruta, nombre)

        if os.path.isdir(ruta_elemento):
            # Caso recursivo: sumar los archivos de la subcarpeta.
            total_archivos = total_archivos + contar_archivos_recursivo(
                ruta_elemento
            )

        elif os.path.isfile(ruta_elemento):
            total_archivos = total_archivos + 1

    return total_archivos


def mostrar_cabecera(consola):
    """Muestra la cabecera.

    Recibe el objeto consola que se utilizará para mostrar el panel.
    No devuelve ningún resultado.
    """
    panel = Panel(
        "Organizador automático de carpetas",
        border_style="cyan",
    )
    consola.print(panel)


def mostrar_informe(consola, movidos, tamano_total, en_origen, en_destino, historial):
    """Muestra el resumen y los movimientos realizados.

    Recibe la consola, el número de archivos movidos, los bytes movidos,
    los recuentos de origen y destino y la lista de movimientos.
    No devuelve ningún resultado.
    """
    # Construir la tabla de resumen.
    resumen = Table(title="Informe final")
    resumen.add_column("Concepto")
    resumen.add_column("Valor", justify="right")

    color_origen = "green" if en_origen == 0 else "red"

    resumen.add_row("Archivos movidos", str(movidos))
    resumen.add_row("Tamaño total movido", tamano_legible(tamano_total))
    resumen.add_row(
        "Archivos que quedan en el origen",
        f"[{color_origen}]{en_origen}[/{color_origen}]",
    )
    resumen.add_row("Archivos en el destino", str(en_destino))

    consola.print(resumen)

    # Construir la tabla del historial.
    movimientos = Table(title="Movimientos realizados")
    movimientos.add_column("N.º", justify="right")
    movimientos.add_column("Origen → destino")

    numero = 1
    for movimiento in historial:
        movimientos.add_row(str(numero), movimiento)
        numero = numero + 1

    consola.print(movimientos)


def main():
    """Inicia el programa.

    No recibe parámetros ni devuelve ningún resultado.
    """
    # Crear una única consola y mostrar la presentación.
    consola = Console()
    mostrar_cabecera(consola)

    # Pedir las rutas de trabajo
    ruta_origen = Prompt.ask(
        "[cyan]Carpeta de origen[/cyan]",
        console=consola,
    )
    ruta_destino = Prompt.ask(
        "[cyan]Carpeta de destino[/cyan]",
        console=consola,
    )

    # Comprobar que el origen existe y es una carpeta
    if not os.path.isdir(ruta_origen):
        consola.print(
            Panel(
                "La ruta de origen no existe o no es una carpeta",
                border_style="red",
            )
        )
        return

    # Si el destino existe, debe ser una carpeta
    if os.path.exists(ruta_destino) and not os.path.isdir(ruta_destino):
        consola.print(
            Panel(
                "La ruta de destino existe, pero no es una carpeta",
                border_style="red",
            )
        )
        return

    # Evita rutas iguales o carpetas contenidas una dentro de otra
    if una_dentro_de_otra(ruta_origen, ruta_destino):
        consola.print(
            Panel(
                "Origen y destino no pueden ser iguales ni estar uno dentro del otro",
                border_style="red",
            )
        )
        return

    historial = []

    # Clasificar los archivos y obtener los bytes movidos
    tamano_total = clasificar_carpeta_recursivo(
        ruta_origen,
        ruta_destino,
        historial,
    )

    # Contar los archivos después de la clasificación
    en_origen = contar_archivos_recursivo(ruta_origen)

    if os.path.isdir(ruta_destino):
        en_destino = contar_archivos_recursivo(ruta_destino)
    else:
        en_destino = 0

    # Mostrar los resultados.
    mostrar_informe(
        consola,
        len(historial),
        tamano_total,
        en_origen,
        en_destino,
        historial,
    )


if __name__ == "__main__":
    main()
