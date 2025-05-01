# This module will handle UML class to PlantUML conversion logic.
from models.uml_models import UmlClass

class UMLToPlantUMLConverter:
    def uml_class_to_plantuml(self, uml_class: UmlClass, uml_model: dict) -> str:
        """Convert an UML class to PlantUML format."""
        puml_str = f"{uml_class.type} {uml_class.name} {{\n"
        puml_str_relationships = ""
        for attr in uml_class.attributes:
            if attr.ref:
                ref_class_name = attr.ref.split("/")[-1]
                if uml_model.get(ref_class_name) and uml_model[ref_class_name].type == "enum":
                    puml_str += f"    +{attr.name} : {attr.type}\n"
                else:
                    puml_str_relationships += f"{uml_class.name} *-- {ref_class_name}\n"
            else:
                icon = "-" if not attr.required else "#"
                puml_str += f"    {icon}{attr.name} : {attr.type}\n"
        puml_str += "}\n"
        puml_str += puml_str_relationships
        return puml_str
    
    def uml_model_to_plantuml(self, uml_model: dict) -> str:
        puml_str = "@startuml\n"
        for class_name, uml_class in uml_model.items():
            puml_str += self.uml_class_to_plantuml(uml_class, uml_model)
        puml_str += "\n@enduml"
        return puml_str
    