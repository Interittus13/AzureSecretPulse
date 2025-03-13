import os
import webbrowser
from jinja2 import Environment, FileSystemLoader

def save_html_preview(html_content, filename="preview.html"):
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    temp_file = os.path.join(output_dir, filename)

    with open(temp_file, "w", encoding="utf-8") as file:
        file.write(html_content)

    webbrowser.open(temp_file)

def render_html_report(data):
    """
    Renders the HTML report using Jinja2.

    :param data: List of Expiring Secrets data
    :return: Rendered HTML report as a string
    """
    TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../templates")
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    template = env.get_template("alert.html")
    alert = template.render(secrets=data)
    save_html_preview(alert)
    return alert