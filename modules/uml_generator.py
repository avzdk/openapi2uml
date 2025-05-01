# This module will handle UML generation logic as a class.
from models.uml_models import UmlClass, UmlClassAttribute
import os
import yaml
from modules.uml_to_plantuml import UMLToPlantUMLConverter

class UMLGenerator:
    def __init__(self, schema_dir):
        self.schema_dir = schema_dir
        self.uml_model = {}

    def _load_yaml(self) -> dict:
        """Load YAML files from the specified directory."""
        yamls = {}
        for file in os.listdir(self.schema_dir):
            if file.endswith(".yaml"):
                with open(os.path.join(self.schema_dir, file), 'r', encoding='utf-8') as f:
                    yamls[file] = yaml.safe_load(f)
        return yamls

    def _schema_to_uml_class(self, name, schema) -> UmlClass:
        """Convert a schema to an UML class representation."""
        uml_class = UmlClass(name=name)
        uml_class.description = schema.get("description", "MISSING")

        if "enum" in schema:
            uml_class.type = "enum"

        for prop_name, prop_details in schema.get("properties", {}).items():
            attribute = UmlClassAttribute(
                name=prop_name,
                type=prop_details.get("type", "unknown"),
                format=prop_details.get("format"),
                description=prop_details.get("description"),
                example=prop_details.get("example"),
                ref=prop_details.get("$ref"),
                required=prop_name in schema.get("required", [])
            )
            uml_class.attributes.append(attribute)

        return uml_class

    def generate_uml(self):
        yamls = self._load_yaml()
        
        for yaml_name, yamldict in yamls.items():
            schemas = yamldict['components']['schemas']
            for schema_name, schema in schemas.items():
                uml_class = self._schema_to_uml_class(schema_name, schema)
                self.uml_model[schema_name] = uml_class
        
        return self.uml_model

