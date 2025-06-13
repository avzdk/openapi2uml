# -*- coding: utf-8 -*-
import argparse
from modules.uml_generator import UMLGenerator
from modules.uml_to_plantuml import UMLToPlantUMLConverter
import plantuml
import subprocess
import os
import sys

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

    python_executable = sys.executable
    
    # Use subprocess to call python -m plantuml directly
    try:
        result = subprocess.run(
            [python_executable, "-m", "plantuml", FILENAME], 
            check=True,
            capture_output=True,
            text=True
        )
        print(f"Diagram generated successfully: diagram.png")
        if os.path.exists("diagram.png"):
            print(f"File size: {os.path.getsize('diagram.png')} bytes")
        else:
            print("Warning: diagram.png was not found")
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate diagram: {e}")
        print(f"Error output: {e.stderr}")