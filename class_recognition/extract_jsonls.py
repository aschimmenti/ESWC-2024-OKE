
import rdflib
from rdflib import RDF, RDFS
import json


output_file = "class-recognition-dataset.jsonl"
subset_output_file = "class-recognition-dataset-subset.jsonl"

# Initialize an RDF graph
g = rdflib.Graph()
g.parse("oke_example.ttl", format="ttl")

# Namespaces
nif = rdflib.Namespace("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#")
itsrdf = rdflib.Namespace("http://www.w3.org/2005/11/its/rdf#")
oke = rdflib.Namespace("http://www.ontologydesignpatterns.org/data/oke-challenge/task-2/")
owl = rdflib.Namespace("http://www.w3.org/2002/07/owl#")
dul = rdflib.Namespace("http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#")

# Assuming the graph has been populated with the provided TTL data

# Function to process the graph based on the specified steps
def process_graph():
    results = []
    
    # Step 1: Find all nif:Context (full sentences)
    contexts = list(g.subjects(RDF.type, nif.Context))
    
    for context in contexts:
        sentence = str(g.value(context, nif.isString))
        sentence_number = context.split("#")[1]
        
        # Step 2: Find substrings related to this context
        substrings = list(g.subjects(nif.referenceContext, context))
        
        # Step 3: Filter substrings with itsrdf:taIdentRef pointing to oke:
        for substring in substrings:
            oke_refs = list(g.objects(substring, itsrdf.taIdentRef))
            oke_refs = [ref for ref in oke_refs if str(ref).startswith(str(oke))]
            
            # Step 4: For each oke_ref, find related owl:Class info
            for oke_ref in oke_refs:
                oke_classes = list(g.triples((oke_ref, RDF.type, owl.Class)))
                for oke_class in oke_classes:
                    class_uri = oke_class[0]
                    label = str(g.value(class_uri, RDFS.label))
                    subclass_of = list(g.objects(class_uri, RDFS.subClassOf))
                    subclass_of_uris = [str(subclass) for subclass in subclass_of]
                    
                    # Compile result
                    result = {
                        "sentence": sentence,
                        "oke_class_uri": str(class_uri),
                        "label": label,
                        "subclass_of": subclass_of_uris
                    }
                    results.append(result)
    
    return results

# Execute the function (assuming RDF data is already loaded)
results = process_graph()

with open(output_file, 'w', encoding='utf-8') as f:
    for result in results:
        # Extract the last field from each subclass URI
        last_fields = [uri.split('/')[-1] for uri in result['subclass_of']]
        
        # Construct the JSON object for the current result
        json_object = {
            "text": f"{result['oke_class_uri'].split('/')[-1]} in the context of this sentence: {result['sentence']}",
            "answer": ", ".join(last_fields)  # Joining the last fields into a single string
        }
        
        # Dump the JSON object as a string in the .jsonl file
        f.write(json.dumps(json_object) + '\n')

print(f"Results have been written to {output_file}")


