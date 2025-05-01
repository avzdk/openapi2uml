# -*- coding: utf-8 -*-
from modules.uml_generator import UMLGenerator

if __name__ == "__main__":
    schema_dir = "./data/schemas"
    uml_generator = UMLGenerator(schema_dir)
    uml_generator.generate_uml()