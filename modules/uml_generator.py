# This module will handle UML generation logic as a class.
from models.uml_models import UmlClass, UmlClassAttribute, UmlRelationship
import os
import yaml
from modules.uml_to_plantuml import UMLToPlantUMLConverter

class UMLGenerator:
    """
    Hovedklasse for at generere UML modeller fra OpenAPI schema filer.
    
    Denne klasse håndterer indlæsning af YAML filer, konvertering til UML klasser,
    og oprettelse af relationships mellem klasserne baseret på OpenAPI specifikationer.
    
    Understøtter:
    - Almindelige properties og attributter
    - Enum håndtering
    - Array relationships
    - oneOf/anyOf polymorfiske relationships med abstract klasser
    - allOf inheritance relationships
    """
    def __init__(self, schema_dir):
        """
        Initialiserer UML generator med schema directory.
        
        Args:
            schema_dir (str): Sti til directory der indeholder OpenAPI schema YAML filer
        """
        self.schema_dir = schema_dir
        self.uml_model : dict[str, UmlClass] = {}  # Dictionary af alle UML klasser
        self.uml_relationships: list[UmlRelationship] = []  # Liste af alle relationships 

    def _load_yaml(self) -> dict:
        """
        Indlæser YAML filer fra det specificerede directory (kun top-level).
        
        BEMÆRK: Denne metode bruges ikke i den nuværende implementation.
        Se _load_yaml_recursive() for den aktive metode.
        
        Returns:
            dict: Dictionary med filnavn som nøgle og parsed YAML indhold som værdi
        """
        yamls = {}
        for file in os.listdir(self.schema_dir):
            if file.endswith(".yaml"):
                with open(os.path.join(self.schema_dir, file), 'r', encoding='utf-8') as f:
                    yamls[file] = yaml.safe_load(f)
        return yamls
    
    def _load_yaml_recursive(self) -> dict:
        """
        Indlæser rekursivt alle YAML filer fra schema directory og subdirectories.
        
        Går gennem alle filer og mapper og finder .yaml filer der indeholder
        'components/schemas' struktur. Dette sikrer at kun valide OpenAPI
        schema filer bliver indlæst.
        
        Returns:
            dict: Dictionary med filnavn som nøgle og parsed YAML indhold som værdi.
                  Kun filer med valid OpenAPI schema struktur inkluderes.
        
        Side effects:
            - Printer filnavne der bliver indlæst
            - Filtrerer filer der ikke har components/schemas struktur
        """
        yamls = {}
        for root, _, files in os.walk(self.schema_dir):
            for file in files:
                if file.endswith(".yaml"):
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        print(f"Loading YAML file: {file}")
                        loaded = yaml.safe_load(f)
                        if 'components' in loaded and 'schemas' in loaded['components']:
                            yamls[file] = loaded
        return yamls

    def _schema_to_uml_class(self, name: str, schema: dict) -> UmlClass:
        """
        Konverterer et enkelt OpenAPI schema til en UML klasse.
        
        Håndterer følgende OpenAPI elementer:
        - Enum schemas (markeres med type="enum")
        - Almindelige properties med type, format, description, example
        - Required fields (markeres på attributterne)
        - Komplekse typer som arrays, references, oneOf, anyOf (logges men håndteres i relationships)
        
        Args:
            name (str): Navnet på schema/klassen
            schema (dict): OpenAPI schema definition
            
        Returns:
            UmlClass: UML klasse repræsentation af schema
            
        Side effects:
            - Printer beskeder om komplekse typer der springes over i denne fase
            - Konverterer example værdier til strings
        """
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
                # her springes Enum over
            elif prop_details.get("oneOf"):
                print(f"OneOf type detected for {prop_name}.")

            elif prop_details.get("anyOf"):
                print(f"AnyOf type detected for {prop_name}.")

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
    
    def _handle_enum(self, schema_name, prop_name) -> None:
        """
        Håndterer enum properties ved at tilføje dem som attributter til den eksisterende klasse.
        
        Når en property refererer til en enum (detekteret via '$ref' der indeholder 'enum'),
        tilføjes enum'en som en attribut direkte på klassen i stedet for som en separat relationship.
        
        Args:
            schema_name (str): Navnet på den klasse der skal have enum attributten
            prop_name (str): Navnet på property'en der refererer til enum'en
            
        Side effects:
            - Modificerer eksisterende UML klasse ved at tilføje enum attribut
            - Printer besked om enum håndtering
        """
        print(f"Enum handled detected for {schema_name}.")
        uc = self.uml_model[schema_name]
        uc.attributes.append(
            UmlClassAttribute(
                name=prop_name,
                type="enum",
                required=False
            )
        )

    
    def _find_relationships(self, schema_name, schema) -> list[UmlRelationship]:
        """
        Finder og opretter alle relationships for et given schema.
        
        Håndterer følgende typer af relationships:
        1. Direkte $ref relationships (aggregation)
        2. Enum references (håndteres som attributter via _handle_enum)
        3. Array relationships (delegeres til _handle_array_items)
        4. oneOf relationships (delegeres til _handle_polymorphic_relationship med multiplicity="1")
        5. anyOf relationships (delegeres til _handle_polymorphic_relationship med multiplicity="*")
        
        Args:
            schema_name (str): Navnet på schema der skal analyseres
            schema (dict): Schema definition der skal analyseres for relationships
            
        Returns:
            list[UmlRelationship]: Liste af alle relationships fundet i schema
            
        Side effects:
            - Kalder _handle_enum for enum references
            - Printer beskeder om fundne relationship typer
        """
        relationships = []
        for prop_name, prop_details in schema.get("properties", {}).items():
            if "$ref" in prop_details:
                if "enum" in prop_details.get("$ref", ""):
                    print(f"Enum type detected for {prop_name}.")
                    self._handle_enum(schema_name, prop_name)
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
                        name=prop_name,
                        multiplicitySource="1",
                        multiplicityTarget=multiplicityTarget
                    )
                    relationships.append(relationship)
            elif prop_details.get("type") == "array":
                relationships.extend(self._handle_array_items(schema_name, prop_name, prop_details.get("items", {})))
            elif prop_details.get("oneOf") is not None:
                print(f"OneOf type detected for {prop_name}.")
                relationships.extend(
                    self._handle_polymorphic_relationship(schema_name, prop_name, prop_details["oneOf"], "oneOf", "1")
                )
            elif prop_details.get("anyOf") is not None:
                print(f"AnyOf type detected for {prop_name}.")
                relationships.extend(
                    self._handle_polymorphic_relationship(schema_name, prop_name, prop_details["anyOf"], "anyOf", "*")
                )

            
        return relationships

    def _create_oneof_abstract_class(self, prop_name: str, one_of_refs: list) -> str:
        """
        Opretter en abstrakt klasse for oneOf/anyOf relationships.
        
        Navnet på den abstrakte klasse bestemmes ved:
        1. Først: Find fælles prefix blandt de konkrete klassnavne (mindst 2 karakterer)
        2. Fallback: Brug property navnet hvis intet fælles prefix findes
        
        Args:
            prop_name (str): Navnet på property'en der har oneOf/anyOf (fallback navn)
            one_of_refs (list): Liste af $ref objekter der peger på konkrete klasser
            
        Returns:
            str: Navnet på den oprettede (eller eksisterende) abstrakte klasse
            
        Side effects:
            - Opretter ny UmlClass med type="abstract" hvis den ikke eksisterer
            - Tilføjer klassen til self.uml_model
            - Printer besked om oprettelse af abstrakt klasse og navngivningsstrategi
            
        Eksempel:
            Klasser: ["SpecD", "SpecE"] -> abstract_class_name="Spec"
            Klasser: ["A", "B"] -> abstract_class_name="OneofRelation" (fra prop_name)
        """
        # Extract class names from references
        class_names = []
        for ref in one_of_refs:
            if "$ref" in ref:
                class_name = ref["$ref"].split("/")[-1]
                class_names.append(class_name)
        
        # Try to find common prefix among class names
        common_prefix = self._find_common_prefix(class_names)
        
        if common_prefix:
            abstract_class_name = common_prefix
            print(f"Using common prefix '{common_prefix}' from classes {class_names} for abstract class")
        else:
            # Fallback to property name
            abstract_class_name = f"{prop_name.replace('_', '').title()}"
            print(f"No common prefix found in classes {class_names}, using property name '{prop_name}' -> '{abstract_class_name}'")
        
        # Check if the abstract class already exists
        if abstract_class_name not in self.uml_model:
            abstract_class = UmlClass(
                name=abstract_class_name,
                type="abstract",
                description=f"Abstract class for oneOf/anyOf property '{prop_name}' generalizing {class_names}"
            )
            self.uml_model[abstract_class_name] = abstract_class
            print(f"Created abstract class: {abstract_class_name}")
        
        return abstract_class_name

    def _find_allof_relationships(self, schema_name: str, schema: dict) -> list[UmlRelationship]:
        """
        Finder og opretter inheritance relationships baseret på allOf konstruktioner.
        
        I OpenAPI betyder allOf at et schema arver/udvider fra et eller flere andre schemas.
        Dette oversættes til UML inheritance relationships hvor den nuværende klasse
        (child) arver fra de refererede klasser (parents).
        
        Args:
            schema_name (str): Navnet på schema der potentielt har allOf
            schema (dict): Schema definition der skal tjekkes for allOf
            
        Returns:
            list[UmlRelationship]: Liste af inheritance relationships, tom hvis ingen allOf
            
        Side effects:
            - Printer beskeder om fundne allOf konstruktioner og oprettede inheritance relationships
            
        Eksempel:
            Schema "Aext" med allOf: [{ $ref: "./A.yaml#/components/schemas/A" }]
            -> Opretter inheritance: Aext --|> A
        """
        relationships = []
        if "allOf" in schema:
            print(f"AllOf detected for {schema_name}.")
            for all_of_item in schema["allOf"]:
                if "$ref" in all_of_item:
                    target_class_name = all_of_item["$ref"].split("/")[-1]
                    # Create inheritance relationship (child inherits from parent)
                    inheritance_relationship = UmlRelationship(
                        source=self.uml_model[schema_name],  # Child class
                        target=self.uml_model[target_class_name],  # Parent class
                        type="generalization",
                        name=None,
                        multiplicitySource=None,
                        multiplicityTarget=None
                    )
                    relationships.append(inheritance_relationship)
                    print(f"Created inheritance: {schema_name} inherits from {target_class_name}")
        return relationships

    def _handle_polymorphic_relationship(self, schema_name: str, prop_name: str, poly_refs: list, relationship_type: str, multiplicity_target: str) -> list[UmlRelationship]:
        """
        Håndterer oneOf/anyOf polymorfiske relationships ved at oprette abstract klasse og inheritance.
        
        Dette er kernen i oneOf/anyOf håndtering:
        1. Opretter en abstrakt klasse baseret på property navnet
        2. Opretter aggregation relationship fra parent klasse til abstrakt klasse
        3. Opretter inheritance relationships fra alle konkrete klasser til abstrakt klasse
        
        Args:
            schema_name (str): Navnet på parent klassen der har oneOf/anyOf property
            prop_name (str): Navnet på property'en (bruges til abstrakt klasse navn)
            poly_refs (list): Liste af $ref objekter der peger på konkrete klasser
            relationship_type (str): "oneOf" eller "anyOf" (til dokumentation)
            multiplicity_target (str): "1" for oneOf, "*" for anyOf
            
        Returns:
            list[UmlRelationship]: Liste indeholdende:
                - 1 aggregation relationship (parent -> abstract)
                - N inheritance relationships (concrete -> abstract)
                
        Side effects:
            - Kalder _create_oneof_abstract_class som opretter abstrakt klasse
            
        Eksempel:
            oneOf: [ClassA, ClassB] -> 
            - Abstrakt klasse "PropertyName"
            - Parent o-- "1" PropertyName
            - ClassA --|> PropertyName
            - ClassB --|> PropertyName
        """
        relationships = []
        
        # Create abstract class for the polymorphic relationship
        abstract_class_name = self._create_oneof_abstract_class(prop_name, poly_refs)
        
        # Create aggregation relationship to the abstract class
        relationship = UmlRelationship(
            source=self.uml_model[schema_name],
            target=self.uml_model[abstract_class_name],
            type="aggregation",
            name=prop_name,
            multiplicitySource="1",
            multiplicityTarget=multiplicity_target
        )
        relationships.append(relationship)
        
        # Create inheritance relationships from concrete classes to abstract class
        for poly_ref in poly_refs:
            if "$ref" in poly_ref:
                target_class_name = poly_ref["$ref"].split("/")[-1]
                inheritance_relationship = UmlRelationship(
                    source=self.uml_model[target_class_name],
                    target=self.uml_model[abstract_class_name],
                    type="generalization",
                    name=None,
                    multiplicitySource=None,
                    multiplicityTarget=None
                )
                relationships.append(inheritance_relationship)
        
        return relationships

    def _handle_array_items(self, schema_name: str, prop_name: str, items: dict) -> list[UmlRelationship]:
        """
        Håndterer forskellige typer af array items og opretter passende relationships.
        
        Arrays kan indeholde forskellige typer af items:
        1. anyOf items -> Delegeres til _handle_polymorphic_relationship med multiplicity="*"
        2. oneOf items -> Delegeres til _handle_polymorphic_relationship med multiplicity="*"
        3. allOf items -> Logges men ikke implementeret endnu
        4. Direkte $ref -> Opretter simpel aggregation med multiplicity="*"
        
        Args:
            schema_name (str): Navnet på klassen der har array property'en
            prop_name (str): Navnet på array property'en
            items (dict): Items definition fra array schema
            
        Returns:
            list[UmlRelationship]: Liste af relationships afhængig af items type:
                - Polymorfiske: Aggregation + inheritance relationships
                - Direkte ref: Enkelt aggregation relationship
                - allOf: Tom liste (ikke implementeret)
                
        Side effects:
            - Printer beskeder om fundne array item typer
            - For anyOf/oneOf: Opretter abstrakt klasse via _handle_polymorphic_relationship
            
        Bemærk:
            Arrays får altid multiplicity="*" da det er en array af elementer.
        """
        relationships = []
        
        if items.get("anyOf") is not None:
            print(f"Array type with AnyOf detected for {prop_name}.")
            relationships.extend(
                self._handle_polymorphic_relationship(schema_name, prop_name, items["anyOf"], "anyOf", "*")
            )
        elif items.get("oneOf") is not None:
            print(f"Array type with OneOf detected for {prop_name}.")
            relationships.extend(
                self._handle_polymorphic_relationship(schema_name, prop_name, items["oneOf"], "oneOf", "*")
            )
        elif items.get("AllOf") is not None:
            print(f"Array type with AllOf detected for {prop_name}.")
            # TODO: Implement allOf handling for arrays if needed
        elif items.get("$ref") is not None:
            ref = items.get("$ref")
            if ref:
                target_class_name = ref.split("/")[-1]
                print(f"Array with direct reference to {target_class_name}")
                relationship = UmlRelationship(
                    source=self.uml_model[schema_name],
                    target=self.uml_model[target_class_name],
                    type="aggregation",
                    name=prop_name,
                    multiplicitySource="1",
                    multiplicityTarget="*"
                )
                relationships.append(relationship)
        
        return relationships

    def _find_common_prefix(self, class_names: list[str]) -> str:
        """
        Finder det fælles prefix blandt en liste af klassnavne.
        
        Args:
            class_names (list[str]): Liste af klassnavne
            
        Returns:
            str: Det fælles prefix, eller tom streng hvis ingen fælles prefix
            
        Eksempel:
            ["SpecD", "SpecE"] -> "Spec"
            ["ClassA", "ClassB"] -> "Class"
            ["PersonInfo", "PersonData"] -> "Person"
            ["A", "B"] -> ""
        """
        if not class_names or len(class_names) < 2:
            return ""
        
        # Find det korteste navn for at undgå index fejl
        min_length = min(len(name) for name in class_names)
        if min_length == 0:
            return ""
        
        # Find fælles prefix
        common_prefix = ""
        for i in range(min_length):
            char = class_names[0][i]
            if all(name[i] == char for name in class_names):
                common_prefix += char
            else:
                break
        
        # Kun returner prefix hvis det er meningsfuldt (mindst 2 karakterer)
        return common_prefix if len(common_prefix) >= 2 else ""

    def generate_uml(self) -> tuple[dict[str, UmlClass], list[UmlRelationship]]:
        """
        Hovedmetode der genererer komplet UML model fra alle YAML schema filer.
        
        Processen sker i tre faser:
        1. Indlæs alle YAML filer rekursivt
        2. Opret UML klasser for alle schemas (første gennemgang)
        3. Opret relationships mellem klasserne (anden gennemgang)
        
        To-faset approach sikrer at alle klasser eksisterer før relationships oprettes,
        hvilket undgår problemer med forward references.
        
        Returns:
            tuple: (uml_model, uml_relationships) hvor:
                - uml_model: Dict[str, UmlClass] - Alle UML klasser indexeret efter navn
                - uml_relationships: List[UmlRelationship] - Alle relationships mellem klasser
                
        Side effects:
            - Populerer self.uml_model med alle UML klasser
            - Populerer self.uml_relationships med alle relationships
            - Printer beskeder om indlæsning via _load_yaml_recursive
            
        Fejlhåndtering:
            - Forventer at alle $ref references peger på eksisterende klasser
            - Ignorerer filer uden valid OpenAPI struktur
        """
        yamls = self._load_yaml_recursive()
        
        for yaml_name, yamldict in yamls.items():
            schemas = yamldict['components']['schemas']
        # Iterate through each schema in the YAML file and convert it to UML class
            for schema_name, schema in schemas.items():
                uml_class = self._schema_to_uml_class(schema_name, schema)
                self.uml_model[schema_name] = uml_class
        # Iterate through each schema in the YAML file and find relationships
        # handles enum and arrays
        all_relationships = []
        for yaml_name, yamldict in yamls.items():
            schemas = yamldict['components']['schemas']
            for schema_name, schema in schemas.items():
                relationships = self._find_relationships(schema_name, schema)
                all_relationships.extend(relationships)
                allof_relationships = self._find_allof_relationships(schema_name, schema)
                all_relationships.extend(allof_relationships)
        
        # Remove duplicate generalization relationships
        # (can happen when multiple oneOf/anyOf properties use the same classes)
        unique_relationships = []
        generalization_seen = set()  # (source, target) tuples for generalization relationships
        
        for rel in all_relationships:
            if rel.type == "generalization":
                rel_key = (rel.source.name, rel.target.name)
                if rel_key not in generalization_seen:
                    generalization_seen.add(rel_key)
                    unique_relationships.append(rel)
                else:
                    print(f"Skipping duplicate generalization: {rel.source.name} --|> {rel.target.name}")
            else:
                unique_relationships.append(rel)
        
        self.uml_relationships = unique_relationships
        return self.uml_model, self.uml_relationships

