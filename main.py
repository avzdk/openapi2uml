# -*- coding: utf-8 -*-
import argparse
from modules.uml_generator import UMLGenerator
from modules.uml_to_plantuml import UMLToPlantUMLConverter

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate UML diagrams from OpenAPI schemas.")
    parser.add_argument("schema_dir", type=str, help="Path to the directory containing OpenAPI schemas.")
    args = parser.parse_args()

    uml_generator = UMLGenerator(args.schema_dir)
    model = uml_generator.generate_uml()
    pluml_converter = UMLToPlantUMLConverter()
    pumlstr = pluml_converter.uml_model_to_plantuml(model)

    FILENAME = "diagram.puml"
    with open(FILENAME, "w") as f:
        f.write(pumlstr)
    print(f"PlantUML string generated to {FILENAME}")
