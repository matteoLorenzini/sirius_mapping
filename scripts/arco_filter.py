from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD, DC, DCTERMS

# ---------------------------
#  DEFINE ALL NAMESPACES
# ---------------------------
rdf           = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs          = Namespace("http://www.w3.org/2000/01/rdf-schema#")
dc            = Namespace("http://purl.org/dc/elements/1.1/")
dcterms       = Namespace("http://purl.org/dc/terms/")
owl           = Namespace("http://www.w3.org/2002/07/owl#")
xsd           = Namespace("http://www.w3.org/2001/XMLSchema#")
cis           = Namespace("http://dati.beniculturali.it/cis/")
foaf          = Namespace("http://xmlns.com/foaf/0.1/")
skos          = Namespace("http://www.w3.org/2004/02/skos/core#")
geo           = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
SAN           = Namespace("http://dati.san.beniculturali.it/SAN/")
oad           = Namespace("http://lod.xdams.org/reload/oad/")
crm           = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
ICCDfoto      = Namespace("http://dati.beniculturali.it/iccd/fotografico/")
accessCond    = Namespace("https://w3id.org/italia/onto/AccessCondition/")
potapit       = Namespace("https://w3id.org/italia/onto/POT/")
smapit        = Namespace("https://w3id.org/italia/onto/SM/")
tiapit        = Namespace("https://w3id.org/italia/onto/TI/")
l0            = Namespace("https://w3id.org/italia/onto/l0/")
roapit        = Namespace("https://w3id.org/italia/onto/RO/")
clvapit       = Namespace("https://w3id.org/italia/onto/CLV/")
cpevapit      = Namespace("https://w3id.org/italia/onto/CPEV/")
cpvapit       = Namespace("https://w3id.org/italia/onto/CPV/")
itLang        = Namespace("https://w3id.org/italia/onto/Language/")
itMU          = Namespace("https://w3id.org/italia/onto/MU/")
arco          = Namespace("https://w3id.org/arco/ontology/arco/")
arco_res      = Namespace("https://w3id.org/arco/resource/")
core          = Namespace("https://w3id.org/arco/ontology/core/")
a_loc         = Namespace("https://w3id.org/arco/ontology/location/")
a_cat         = Namespace("https://w3id.org/arco/ontology/catalogue/")
a_dd          = Namespace("https://w3id.org/arco/ontology/denotative-description/")
a_cd          = Namespace("https://w3id.org/arco/ontology/context-description/")
a_ce          = Namespace("https://w3id.org/arco/ontology/cultural-event/")
rico          = Namespace("http://www.ica.org/standards/RiC/ontology#")
covapit       = Namespace("https://w3id.org/italia/onto/COV/")
a_cc          = Namespace("https://w3id.org/arco/ontology/cataloguing-campaign/")
a_cod         = Namespace("https://w3id.org/arco/ontology/construction-description/")
a_ip          = Namespace("https://w3id.org/arco/ontology/immovable-property/")
a_mp          = Namespace("https://w3id.org/arco/ontology/movable-property/")
a_nsd         = Namespace("https://w3id.org/arco/ontology/natural-specimen-description/")
arco_lite     = Namespace("https://w3id.org/arco/ontology/arco-lite/")
pico          = Namespace("http://data.cochrane.org/ontologies/pico/")
geonames      = Namespace("http://www.geonames.org/ontology#")
schema        = Namespace("https://schema.org/")
skosx         = Namespace("http://www.w3.org/2008/05/skos#")

# ---------------------------
# INPUT / OUTPUT
# ---------------------------
INPUT_FILE  = "../RDF/dataset-arco_CatalogueRecordA_emilia-romagna.rdf"
OUTPUT_FILE = "../RDF/filtered_ravenna.rdf"


def extract_uid(graph, entity):
    """Return arco:uniqueIdentifier value."""
    for uid in graph.objects(entity, arco.uniqueIdentifier):
        return str(uid)
    return None


def main():
    g = Graph()
    print("Loading RDF graph...")
    g.parse(INPUT_FILE)

    filtered = Graph()

    # ------------------------------------------------------------
    # BIND ALL NAMESPACES SO OUTPUT NEVER USES ns7:preview, etc.
    # ------------------------------------------------------------
    bindings = {
        "rdf": rdf, "rdfs": rdfs, "dc": dc, "dcterms": dcterms, "owl": owl, "xsd": xsd, "cis": cis,
        "foaf": foaf, "skos": skos, "geo": geo, "SAN": SAN, "oad": oad, "crm": crm,
        "ICCDfoto": ICCDfoto, "accessCondition": accessCond, "potapit": potapit,
        "smapit": smapit, "tiapit": tiapit, "l0": l0, "roapit": roapit, "clvapit": clvapit,
        "cpevapit": cpevapit, "cpvapit": cpvapit, "it-Lang": itLang, "it-MU": itMU,
        "arco": arco, "arco-res": arco_res, "core": core, "a-loc": a_loc,
        "a-cat": a_cat, "a-dd": a_dd, "a-cd": a_cd, "a-ce": a_ce, "rico": rico,
        "covapit": covapit, "a-cc": a_cc, "a-cod": a_cod, "a-ip": a_ip,
        "a-mp": a_mp, "a-nsd": a_nsd, "arco-lite": arco_lite, "pico": pico,
        "geonames": geonames, "schema": schema, "skosx": skosx
    }

    for prefix, ns in bindings.items():
        filtered.bind(prefix, ns)

    # ---------------------------
    # FIND ENTITIES WITH Ravenna
    # ---------------------------
    ravenna = set()
    for s, p, o in g.triples((None, dc.coverage, Literal("Ravenna (RA)"))):
        ravenna.add(s)

    print(f"Found {len(ravenna)} main entities.")

    ids = []
    for entity in ravenna:
        # copy triples of main entity
        for t in g.triples((entity, None, None)):
            filtered.add(t)

        uid = extract_uid(g, entity)
        if uid:
            ids.append(uid)

    # ---------------------------
    # MATCH SUBENTITIES
    # ---------------------------
    print("Collecting sub-entities...")

    for subj, pred, obj in g:
        s = str(subj)
        for uid in ids:
            fragment = f"GraphicOrCartographicDocumentation/{uid}-"
            if fragment in s:
                for t in g.triples((subj, None, None)):
                    filtered.add(t)

    print(f"Final triples: {len(filtered)}")
    filtered.serialize(OUTPUT_FILE, format="xml")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
