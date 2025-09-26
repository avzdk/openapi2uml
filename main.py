# -*- coding: utf-8 -*-
import argparse
from modules.uml_generator import UMLGenerator
from modules.uml_to_plantuml import UMLToPlantUMLConverter
from modules.uml_to_mermaid import UMLToMermaidConverter
import plantuml
import subprocess
import os
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate UML diagrams from OpenAPI schemas.")
    parser.add_argument("schema_dir", type=str, help="Path to the directory containing OpenAPI schemas.")
    parser.add_argument("--filename", "-f", type=str, default="diagram", help="Base filename for output files (without extension). Default: diagram")
    parser.add_argument("--format", choices=["plantuml", "mermaid", "both"], default="both", help="Output format: plantuml, mermaid, or both. Default: both")
    parser.add_argument("--startclass", "-s", type=str, default=None, help="Generate UML for a specific class")
    args = parser.parse_args()

    uml_generator = UMLGenerator(args.schema_dir)
    
    if args.startclass is not None:
        print(f"Generating UML for specific class: {args.startclass}")
        model, relations = uml_generator.get_model_from_class_name(args.startclass)
    else:
        model, relations = uml_generator.generate_uml()

    

    # Generate PlantUML if requested
    if args.format in ["plantuml", "both"]:
        pluml_converter = UMLToPlantUMLConverter()
        pumlstr = pluml_converter.uml_model_to_plantuml(model, relations)
        
        FILENAME_PUML = f"{args.filename}.puml"
        with open(FILENAME_PUML, "w") as f:
            f.write(pumlstr)
        print(f"PlantUML string generated to {FILENAME_PUML}")

        python_executable = sys.executable
        
        # Use subprocess to call python -m plantuml directly
        try:
            result = subprocess.run(
                [python_executable, "-m", "plantuml", FILENAME_PUML], 
                check=True,
                capture_output=True,
                text=True
            )
            print(f"PlantUML diagram generated successfully: {args.filename}.png")
            if os.path.exists(f"{args.filename}.png"):
                print(f"File size: {os.path.getsize(f'{args.filename}.png')} bytes")
            else:
                print(f"Warning: {args.filename}.png was not found")
        except subprocess.CalledProcessError as e:
            print(f"Failed to generate PlantUML diagram: {e}")
            print(f"Error output: {e.stderr}")

    # Generate Mermaid if requested
    if args.format in ["mermaid", "both"]:
        mermaid_converter = UMLToMermaidConverter()
        mermaidstr = mermaid_converter.uml_model_to_mermaid(model, relations)
        
        FILENAME_MERMAID = f"{args.filename}.mmd"
        with open(FILENAME_MERMAID, "w") as f:
            f.write(mermaidstr)
        print(f"Mermaid diagram generated to {FILENAME_MERMAID}")
        print("You can view the Mermaid diagram at: https://mermaid.live/ or use mermaid-cli to generate images")