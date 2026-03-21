from todoist_client import obtener_tareas
from markdown_generator import generar_markdown


def main():
    grupos, fechas_orden = obtener_tareas()
    print(generar_markdown(grupos, fechas_orden))


if __name__ == "__main__":
    main()
