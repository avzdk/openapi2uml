# -*- coding: utf-8 -*-
import argparse
from modules.uml_generator import UMLGenerator

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate UML diagrams from OpenAPI schemas.")
    parser.add_argument("schema_dir", type=str, help="Path to the directory containing OpenAPI schemas.")
    args = parser.parse_args()

    uml_generator = UMLGenerator(args.schema_dir)
    uml_generator.generate_uml()