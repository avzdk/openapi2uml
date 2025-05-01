# OpenAPI to UML

## Overview
This project converts OpenAPI schemas into UML diagrams. It processes YAML files containing OpenAPI schemas and generates PlantUML diagrams to visualize the structure and relationships of the schemas.

## Project Structure
- **`main.py`**: Entry point of the application. It initializes the UML generation process and accepts the schema directory as a command-line argument.
- **`modules/`**: Contains the core logic for UML generation and PlantUML conversion.
  - `uml_generator.py`: Handles the loading of YAML files and conversion of schemas to UML classes.
  - `uml_to_plantuml.py`: Converts UML classes into PlantUML format.
- **`models/`**: Defines the data models for UML classes and attributes.
  - `uml_models.py`: Contains the `UmlClass` and `UmlClassAttribute` models.
- **`data/`**: Contains the input YAML files.
  - `schemas/`: OpenAPI schemas.
  - `enums/`: Enum definitions used in the schemas.
- **`testdata/`**: Additional test YAML files for validation.

## How to Use
1. Place your OpenAPI YAML schemas in the `data/schemas/` directory or any directory of your choice.
2. Run the application with the schema directory as an argument:
   ```bash
   python main.py <schema_dir>
   ```
   Replace `<schema_dir>` with the path to your schema directory.
3. The generated PlantUML diagram will be saved as `diagram.puml` in the root directory.

## Requirements
- Python 3.10 or higher
- Dependencies:
  - `pydantic`
  - `pyyaml`

Install dependencies using:
```bash
pip install -r requirements.txt
```

## Features
- Converts OpenAPI schemas to UML diagrams.
- Supports enums and relationships between schemas.
- Outputs diagrams in PlantUML format.

## Future Improvements
- Add support for more OpenAPI features.
- Improve error handling and validation.
- Add a web interface for uploading schemas and viewing diagrams.

## License
This project is licensed under the MIT License.