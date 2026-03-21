from todoist_client import obtener_tareas
from markdown_generator import generar_markdown
from pdf_generator import generar_pdf


def main():
    grupos, fechas_orden = obtener_tareas()
    contenido = generar_markdown(grupos, fechas_orden)
    print(contenido)
    ruta = generar_pdf(contenido)
    print(f"\nPDF generado: {ruta}")


if __name__ == "__main__":
    main()
