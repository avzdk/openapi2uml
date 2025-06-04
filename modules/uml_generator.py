# This module will handle UML generation logic as a class.
from models.uml_models import UmlClass, UmlClassAttribute, UmlRelationship
import os
import yaml
from modules.uml_to_plantuml import UMLToPlantUMLConverter

class UMLGenerator:
    def __init__(self, schema_dir):
        self.schema_dir = schema_dir
        self.uml_model : dict[str, UmlClass] = {}
        self.uml_relationships: list[UmlRelationship] = [] 
    
    def _load_yaml(self) -> dict:
        """Load YAML files from the specified directory."""
        yamls = {}
        for file in os.listdir(self.schema_dir):
            if file.endswith(".yaml"):
                with open(os.path.join(self.schema_dir, file), 'r', encoding='utf-8') as f:
                    yamls[file] = yaml.safe_load(f)
        return yamls
    
    def _load_yaml_recursive(self) -> dict:
        """Recursively load YAML files from the specified directory."""
        yamls = {}
        for root, _, files in os.walk(self.schema_dir):
            for file in files:
                if file.endswith(".yaml"):
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        print(f"Loading YAML file: {file}")
                        yamls[file] = yaml.safe_load(f)
        return yamls

    def _schema_to_uml_class(self, name, schema) -> UmlClass | list[UmlRelationship]:
        """Convert a schema to an UML class representation.
        and relationships."""
        uml_class = UmlClass(name=name)
        uml_class.description = schema.get("description", "MISSING")

        if "enum" in schema:
            uml_class.type = "enum"

        for prop_name, prop_details in schema.get("properties", {}).items():
            
            if prop_details.get("type") == "array":
                print(f"Array type detected for {prop_name}. Skipping for now.")
                ref_class_name = prop_details.get("items", {}).get("$ref")
                print(f"Ref class name: {ref_class_name}")
            
            elif prop_details.get("$ref"):
                print(f"Reference type detected for {prop_name}. Skipping for now.")

            else:
                attribute = UmlClassAttribute(
                    name=prop_name,
                    type=prop_details.get("type", "unknown"),
                    format=prop_details.get("format"),
                    description=prop_details.get("description"),
                    example=str(prop_details.get("example")),
                    ref=prop_details.get("$ref"),
                    required=prop_name in schema.get("required", [])
                )
                uml_class.attributes.append(attribute)

        return uml_class
    
    def _find_relationships(self, schema_name, schema) -> list[UmlRelationship]:
        """Find relationships between schemas."""
        relationships = []
        for prop_name, prop_details in schema.get("properties", {}).items():
            if "$ref" in prop_details:
                if "enum" in prop_details.get("$ref", ""):
                    print(f"Enum type detected for {prop_name}.")
                else:
                    target_class_name = prop_details["$ref"].split("/")[-1]
                    if prop_details.get("type") == "array":
                        multiplicityTarget = "*"
                    else:
                        multiplicityTarget = "1"

                    relationship = UmlRelationship(
                        source=self.uml_model[schema_name],
                        target=self.uml_model[target_class_name],
                        type="aggregation",
                        multiplicitySource="1",
                        multiplicityTarget=multiplicityTarget
                    )
                    relationships.append(relationship)
            elif prop_details.get("type") == "array":
                if prop_details.get("items", {}).get("anyOf") is not None:
                    print(f"Array type with AnyOf detected for {prop_name}.")
                elif prop_details.get("items", {}).get("oneOf") is not None:
                    print(f"Array type with OneOf detected for {prop_name}.")
                elif prop_details.get("items", {}).get("AllOf") is not None:
                    print(f"Array type with AllOf detected for {prop_name}.")
                elif prop_details.get("items", {}).get("$ref") is not None:  
                    #print(f"Array type detected for {prop_name}.")
                    target_class_name = prop_details.get("items", {}).get("$ref").split("/")[-1]
                    print(f"Target class name: {target_class_name}")
                    relationship = UmlRelationship(
                        source=self.uml_model[schema_name],
                        target=self.uml_model[target_class_name],
                        type="aggregation",
                        multiplicitySource="1",
                        multiplicityTarget="*"
                    )
                    relationships.append(relationship)
            
        return relationships

    def generate_uml(self) -> dict | list[UmlRelationship]:
        yamls = self._load_yaml_recursive()
        
        for yaml_name, yamldict in yamls.items():
            schemas = yamldict['components']['schemas']
        # Iterate through each schema in the YAML file and convert it to UML class
            for schema_name, schema in schemas.items():
                uml_class = self._schema_to_uml_class(schema_name, schema)
                self.uml_model[schema_name] = uml_class
        # Iterate through each schema in the YAML file and find relationships
        for yaml_name, yamldict in yamls.items():
            schemas = yamldict['components']['schemas']
            for schema_name, schema in schemas.items():
                relationships = self._find_relationships(schema_name, schema)
                self.uml_relationships.extend(relationships)
        return self.uml_model, self.uml_relationships

