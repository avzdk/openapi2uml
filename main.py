# -*- coding: utf-8 -*-
import argparse
from modules.uml_generator import UMLGenerator
from modules.uml_to_plantuml import UMLToPlantUMLConverter
import plantuml


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate UML diagrams from OpenAPI schemas.")
    parser.add_argument("schema_dir", type=str, help="Path to the directory containing OpenAPI schemas.")
    args = parser.parse_args()

    uml_generator = UMLGenerator(args.schema_dir)
    model, relations = uml_generator.generate_uml()
    pluml_converter = UMLToPlantUMLConverter()
    pumlstr = pluml_converter.uml_model_to_plantuml(model, relations)

    FILENAME = "diagram.puml"
    with open(FILENAME, "w") as f:
        f.write(pumlstr)
    print(f"PlantUML string generated to {FILENAME}")

    plantuml_server = plantuml.PlantUML(url='http://www.plantuml.com/plantuml')
    try:
        plantuml_server.processes_file(FILENAME)
        print(f"Diagram generated successfully and uploaded to PlantUML server.")
    except Exception as e:
        print(f"Failed to generate diagram: {e}")