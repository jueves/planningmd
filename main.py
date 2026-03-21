from todoist_client import obtener_tareas
from markdown_generator import generar_markdown
from html_generator import generar_html
from pdf_generator import generar_pdf, generar_pdf_desde_html


def main():
    grupos, fechas_orden = obtener_tareas()
    contenido = generar_markdown(grupos, fechas_orden)
    print(contenido)
    html = generar_html(grupos, fechas_orden)
    ruta = generar_pdf_desde_html(html)
    print(f"\nPDF generado: {ruta}")


if __name__ == "__main__":
    main()
