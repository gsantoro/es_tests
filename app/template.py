import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

class Templates:
    def __init__(self, templates_path, mapping_template_name, doc_template_name) -> None:
        env = Environment(
            loader=FileSystemLoader(templates_path), 
            autoescape=select_autoescape(default_for_string=True, default=False))
        
        self.mapping_template = env.get_template(mapping_template_name)
        self.doc_template = env.get_template(doc_template_name)