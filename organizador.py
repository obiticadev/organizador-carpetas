from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
import os
import shutil


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
    unidades = ["bytes", "KB", "MB", "GB"]
    tamano = tamano_bytes
    indice = 0

    while tamano >= 1024 and indice < len(unidades) - 1:
        tamano = tamano / 1024
        indice = indice + 1

    return f"{tamano:.2f} {unidades[indice]}"


def una_dentro_de_otra(ruta_a, ruta_b):
    """Recibe dos rutas y devuelve si son iguales o una contiene a la otra."""
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


def mostrar_cabecera(consola):
    """Muestra la cabecera.

    Recibe el objeto consola que se utilizará para mostrar el panel.
    No devuelve ningún resultado.
    """
    panel = Panel(
        "Organización automático de carpetas",
        border_style="cyan",
    )
    consola.print(panel)


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
                "la ruta de destino existe, pero no es una carpeta",
                border_style="red",
            )
        )
        return

    # Evita rutas iguales o carpetas contenidas una dentro de otra
    if una_dentro_de_otra(ruta_origen, ruta_destino):
        consola.print(
            Panel(
                "Origen y destino no pueder ser iguales ni estar uno dentro de otro",
                border_style="red",
            )
        )
        return


if __name__ == "__main__":
    main()
