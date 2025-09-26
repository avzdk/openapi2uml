# This module will handle UML class to Mermaid Class Diagram conversion logic.
from models.uml_models import UmlClass, UmlRelationship

class UMLToMermaidConverter:
    def uml_class_to_mermaid(self, uml_class: UmlClass, uml_model: dict) -> str:
        """Convert an UML class to Mermaid Class Diagram format."""
        # Handle different class types
        class_name = uml_class.name
        
        # Start class definition
        mermaid_str = f"    class {class_name} {{\n"
        
        # Add attributes
        for attr in uml_class.attributes:
            if attr.ref:
                ref_class_name = attr.ref.split("/")[-1]
                if uml_model.get(ref_class_name) and uml_model[ref_class_name].type == "enum":
                    # For enum references, show as attribute
                    visibility = "+" if attr.required else "-"
                    mermaid_str += f"        {visibility}{attr.name} : {attr.type}\n"
                # Note: Relationships via $ref are handled separately in relationships
            else:
                # Regular attributes
                visibility = "+" if attr.required else "-"
                attr_type = attr.type
                if attr.format:
                    attr_type += f":{attr.format}"
                mermaid_str += f"        {visibility}{attr.name} : {attr_type}\n"
        
        mermaid_str += "    }\n"
        
        # Add class annotations for special types
        if uml_class.type == "abstract":
            mermaid_str += f"    {class_name} : <<abstract>>\n"
        elif uml_class.type == "enum":
            mermaid_str += f"    {class_name} : <<enumeration>>\n"
        
        return mermaid_str
    
    def uml_relationship_to_mermaid(self, relationship: UmlRelationship) -> str:
        """Convert an UML relationship to Mermaid Class Diagram format."""
        source = relationship.source.name
        target = relationship.target.name
        
        if relationship.type == "association":
            return f"    {source} --> {target}\n"
        elif relationship.type == "inheritance" or relationship.type == "generalization":
            return f"    {target} <|-- {source}\n"
        elif relationship.type == "aggregation":
            # Mermaid aggregation with multiplicity and label
            multiplicity = relationship.multiplicityTarget if relationship.multiplicityTarget else ""
            label = relationship.name if relationship.name else ""
            if multiplicity and label:
                return f"    {source} o-- \"{multiplicity}\" {target} :  {label}\n"
            elif multiplicity:
                return f"    {source} o-- \"{multiplicity}\" {target}\n"
            elif label:
                return f"    {source} o-- {target} : {label}\n"
            else:
                return f"    {source} o-- {target}\n"
        elif relationship.type == "composition":
            multiplicity = relationship.multiplicityTarget if relationship.multiplicityTarget else ""
            label = relationship.name if relationship.name else ""
            if multiplicity and label:
                return f"    {source} *--  \"{multiplicity}\" {target} : {label}\n"
            elif multiplicity:
                return f"    {source} *--  \"{multiplicity}\"  {target} : \n"
            elif label:
                return f"    {source} *-- {target} : \"{label}\n"
            else:
                return f"    {source} *-- {target}\n"
        else:
            # Default to association
            return f"    {source} --> {target}\n"
    
    def uml_model_to_mermaid(self, uml_model: dict, uml_relationships: list) -> str:
        """Convert complete UML model to Mermaid Class Diagram format."""
        mermaid_str = "classDiagram\n"
        
        # Add only classes that have attributes or are not abstract/empty
        for class_name, uml_class in uml_model.items():
            if uml_class.type not in ["enum"]:  # Exclude enums as separate classes
                # Only add class definition if it has attributes
                if uml_class.attributes:
                    mermaid_str += self.uml_class_to_mermaid(uml_class, uml_model)
                    mermaid_str += "\n"
                elif uml_class.type == "abstract":
                    # For abstract classes without attributes, only add the annotation
                    mermaid_str += f"    class {class_name}\n"
                    mermaid_str += f"    {class_name} : <<abstract>>\n\n"
        
        # Add relationships (this will implicitly reference classes without definitions)
        for relationship in uml_relationships:
            mermaid_str += self.uml_relationship_to_mermaid(relationship)
        
        return mermaid_str
