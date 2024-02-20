import os
import json
import os
import json
import spacy
import rdflib
from rdflib import URIRef, Namespace, RDF, RDFS, OWL

def serialize_relationships_as_ttl(relationships):
    # Define the namespaces
    oke = Namespace("http://example.org/oke#")
    dolce = Namespace("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#")

    # Create a new RDF graph
    g = rdflib.Graph()

    # Bind prefixes for nicer Turtle output
    g.bind("oke", oke)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)
    g.bind("dul", dolce)

    # Iterate over the relationships to add them to the graph
    for rel in relationships:
        subject_uri = oke[rel['subject']['text'].replace(" ", "_")]  # Replace spaces with underscores for valid URIs
        object_class = rel['object']['text']
        object_uri = oke[object_class.replace(" ", "_")]

        # Add rdf:type relationship
        g.add((subject_uri, RDF.type, object_uri))

        # Add rdfs:label for subjects and objects
        g.add((subject_uri, RDFS.label, rdflib.Literal(rel['subject']['text'])))
        g.add((object_uri, RDFS.label, rdflib.Literal(object_class)))

        # Handle subClassOf relationships
        for subclass in rel['object'].get('subClassOf', []):
            subclass_uri = dolce[subclass]  # Assuming subclass names are valid as is
            g.add((object_uri, RDFS.subClassOf, subclass_uri))
            # Optionally add a label for the subclass, if needed
            g.add((subclass_uri, RDFS.label, rdflib.Literal(subclass)))

    # Serialize the graph to Turtle format and return it
    return g.serialize(format="turtle").encode("utf-8")

# Example relationships
relationships = [
    {'subject': {'text': 'La casta'}, 'property': 'rdf:type', 'object': {'text': 'journalist', 'subClassOf': ['PERSON']}},
    {'subject': {'text': 'Sergio Rizzo'}, 'property': 'rdf:type', 'object': {'text': 'journalist', 'subClassOf': ['PERSON']}},
    # Add more relationships as needed...
]

# Serialize and print the RDF Turtle representation

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

def to_singular(text):
    # Process the text through spaCy to get a Doc object
    doc = nlp(text)
    
    # Initialize an empty list to hold the lemmatized tokens
    lemmatized_tokens = []
    
    # Iterate over the tokens in the Doc
    for token in doc:
        # Check if the token is a noun (this includes proper nouns)
        if token.pos_ in ['NOUN', 'PROPN']:
            # Use the lemma_ attribute to get the singular form of the noun/proper noun
            lemmatized_tokens.append(token.lemma_)
        else:
            # For non-noun tokens, use the original text
            lemmatized_tokens.append(token.text)
    
    # Join the tokens back into a string and return
    return ' '.join(lemmatized_tokens)


def check_rel_domain_range(relationship, entities, classes):
    # Extract subject and object text for comparison
    subject_text = relationship['subject']['text']
    object_text = relationship['object']['text']

    # Initialize subClassOf as None
    subClassOf = None

    # Check if the subject is in entities
    subject_in_entities = any(subject_text == ent['text'] for ent in entities)
    
    # Find the class object and check if the object is in classes
    object_in_classes = False
    for cls in classes:
        if object_text == cls['text']:
            object_in_classes = True
            subClassOf = cls.get('subClassOf', None)  # Fetch subClassOf if the object matches a class
            break  # Exit the loop once the matching class is found

    return subject_in_entities and object_in_classes, subClassOf

def open_and_process_json_files(folder_path):
    # List all files in the given folder
    files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    
    # Loop through the files
    for file_name in files:
        # Construct full file path
        file_path = os.path.join(folder_path, file_name)
        
        # Open and read the JSON file
        with open(file_path, 'r', encoding="utf-8") as file:
            data = json.load(file)
            sentence = data['text']
            unique_entities = {}
            unique_classes = {}
            relationships = []  # Initialize the relationships array
            
            # Process entities and classes
            for ent in data['ents']:
                # Skip if no 'text'
                if 'text' not in ent:
                    continue
                
                start = ent.get('start', ent.get('start_char'))
                end = ent.get('end', ent.get('end_char'))
                label = ent.get('label')
                key = (start, end)
                ent['start'] = start
                ent['end'] = end

                if label == 'CLASS':
                    unique_classes[key] = ent
                else:
                    unique_entities[key] = ent
            
            entities = list(unique_entities.values())
            classes = list(unique_classes.values())
            
            # Process relationships
            if 'relations' in data:
                for rel in data['relations']:
                    dep_text = rel.get('dep_text', '')                            
                    dest_text = rel.get('dest_text', '')
                    relation = rel.get('rel', '')  # Removed the trailing comma
                    
                    # Properly check the relation type
                    if relation == 'rdf-isClassOf':
                        relationship_repr = {'subject': {'text': dest_text}, 'property' : 'rdf:type', 'object': {'text': dep_text}}
                    else:
                        relationship_repr = {'subject': {'text': dep_text}, 'property' : 'rdf:type', 'object': {'text': dest_text}}
                    
                    checkdr, subClassOf = check_rel_domain_range(relationship_repr, entities, classes)
                    if checkdr:
                        # Use to_singular for object text
                        relationship_repr['object']['text'] = to_singular(relationship_repr['object']['text'])
                        
                        # Ensure subClassOf is correctly handled
                        if subClassOf:
                            relationship_repr['object']['subClassOf'] = [subClass.title() for subClass in subClassOf]
                        
                        relationships.append(relationship_repr)


            # Demonstration printouts
            print(f"Entities from {file_name}: {entities}")
            print(f"Classes from {file_name}: {classes}")
            print(f"Relationships from {file_name}: {relationships}")
            
            rdf_output = serialize_relationships_as_ttl(relationships)
            
            # Save the RDF Turtle to a file
            ttl_file_name = file_name.rsplit('.', 1)[0] + '.ttl'
            ttl_file_path = os.path.join(folder_path, ttl_file_name)
            with open(ttl_file_path, 'wb') as ttl_file:
                ttl_file.write(rdf_output)
            break
# Example usage:
open_and_process_json_files('./')

