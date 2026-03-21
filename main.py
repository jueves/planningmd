from todoist_client import get_tasks
from markdown_generator import generate_markdown
from html_generator import generate_html
from pdf_generator import generate_pdf


def main():
    groups, dates_order, subtasks_by_parent = get_tasks()
    content = generate_markdown(groups, dates_order)
    print(content)
    html = generate_html(groups, dates_order, subtasks_by_parent)
    path = generate_pdf(html)
    print(f"\nPDF generated: {path}")


if __name__ == "__main__":
    main()
