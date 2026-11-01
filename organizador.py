from rich.console import Console
from rich.panel import Panel


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


if __name__ == "__main__":
    main()
