import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

class Templates:
    def __init__(self) -> None:
        templates_path = os.getenv("TEMPLATES_PATH")

        env = Environment(
            loader=FileSystemLoader(templates_path), 
            autoescape=select_autoescape(default_for_string=True, default=False))
        
        self.mapping_template = env.get_template("mapping.txt")
        self.doc_template = env.get_template("doc.txt")