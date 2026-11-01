from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
import os


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
