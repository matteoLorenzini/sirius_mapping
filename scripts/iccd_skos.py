import pandas as pd
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, SKOS
import re 

def create_skos_thesaurus_ordered(excel_file_path, output_file_path_ttl, output_file_path_rdf):
    """
    Converts an Excel sheet into a SKOS thesaurus, preserving the order 
    of concepts and relations as they appear in the Excel rows.
    """
    try:
        df = pd.read_excel(excel_file_path, header=0)
    except FileNotFoundError:
        print(f"❌ Error: File not found at {excel_file_path}")
        return

    # --- Configuration (Same as before) ---
    EXPLICIT_DEFINITIONS = {
        df.columns[0]: "Categoria Generale",
        df.columns[1]: "Settore Disciplinare",
        df.columns[2]: "Tipo Bene",
        df.columns[3]: "Categoria Disciplinare",
        df.columns[4]: "Definizione",
        df.columns[5]: "Tipologia",
        df.columns[6]: "Note"
    }

    HIERARCHY_COLS = df.columns[:6].tolist()
    NOTE_COL = df.columns[6]
    FILTER_TERM = 'BENI IMMOBILI'
    
    col_A_name = df.columns[0]
    data_df = df.iloc[1:].copy()
    data_df = data_df[data_df[col_A_name] == FILTER_TERM].reset_index(drop=True)
    
    if data_df.empty:
        print(f"⚠️ Warning: No rows found with '{FILTER_TERM}' in column '{col_A_name}'.")
        return

    # --- RDF/SKOS Generation ---
    BASE_URI = Namespace("http://example.org/thesaurus/")
    g = Graph()
    g.bind("skos", SKOS)
    g.bind("", BASE_URI)

    def term_to_uri(term):
        if pd.isna(term) or term is None:
            return None
        slug = str(term).strip().lower()
        slug = re.sub(r'[^a-z0-9_]+', '_', slug)
        slug = re.sub(r'__+', '_', slug)
        slug = slug.strip('_')
        return BASE_URI[slug]

    # Process data rows and add triples to the graph in order
    for index, row in data_df.iterrows():
        prev_concept_uri = None
        
        # 🚨 KEY CHANGE: The serialization order is maintained by adding triples
        # for a row to the graph before processing the next row.
        
        # Process hierarchy from COL A to COL F
        for col_name in HIERARCHY_COLS:
            current_term_raw = row[col_name]
            
            if pd.notna(current_term_raw):
                # 🚨 NEW STEP: Remove square brackets and convert to string
                current_term = str(current_term_raw).replace('[', '').replace(']', '').strip()
                
                # If the term becomes empty after stripping, skip it
                if not current_term:
                    continue

                current_concept_uri = term_to_uri(current_term)
                
                # Concept Type and Label
                g.add((current_concept_uri, RDF.type, SKOS.Concept))
                g.add((current_concept_uri, SKOS.prefLabel, Literal(current_term, lang="it")))
                
                # Definition
                definition_text = EXPLICIT_DEFINITIONS.get(col_name)
                if definition_text:
                    g.add((current_concept_uri, SKOS.definition, Literal(definition_text, lang="it")))

                # Broader/Narrower relationship
                if prev_concept_uri is not None:
                    g.add((current_concept_uri, SKOS.broader, prev_concept_uri))
                    g.add((prev_concept_uri, SKOS.narrower, current_concept_uri))
                    
                prev_concept_uri = current_concept_uri
            
        # Add skos:note (from COL G) to the last concept in the chain
        if prev_concept_uri is not None:
            note_content = row[NOTE_COL]
            if pd.notna(note_content) and str(note_content).strip():
                g.add((prev_concept_uri, SKOS.note, Literal(str(note_content), lang="it")))


    # --- Save the graph in multiple formats ---
    
    # 1. Save as Turtle (.ttl)
    # The serialization output will reflect the order in which the triples were added above.
    g.serialize(destination=output_file_path_ttl, format="turtle")
    print(f"✅ SKOS thesaurus saved successfully as Turtle (.ttl) to {output_file_path_ttl} (Ordered)")
    
    # 2. Save as RDF/XML (.rdf)
    g.serialize(destination=output_file_path_rdf, format="xml")
    print(f"✅ SKOS thesaurus saved successfully as RDF/XML (.rdf) to {output_file_path_rdf} (Ordered)")

# --- Execution ---
excel_path = '../ICCD/beni_culturali.xlsx'
output_path_ttl = 'skos_thesaurus.ttl'
output_path_rdf = 'skos_thesaurus.rdf'

create_skos_thesaurus_ordered(excel_path, output_path_ttl, output_path_rdf)