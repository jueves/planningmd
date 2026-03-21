import argparse
from todoist_client import obtener_tareas
from markdown_generator import generar_markdown
from pdf_generator import generar_pdf


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--details", action="store_true", help="Mostrar etiquetas y descripción de cada tarea")
    args = parser.parse_args()

    grupos, fechas_orden = obtener_tareas()
    contenido = generar_markdown(grupos, fechas_orden, modo_detalles=args.details)
    print(contenido)
    ruta = generar_pdf(contenido)
    print(f"\nPDF generado: {ruta}")


if __name__ == "__main__":
    main()
