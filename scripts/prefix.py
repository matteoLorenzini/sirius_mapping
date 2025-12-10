from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import SKOS, RDF

# Input and output file names
INPUT = "thesaurus_agenti_eventi.ttl"
OUTPUT = "thesaurus_agenti_eventi_prefix.ttl"

# Namespaces
AGENT = Namespace("https://w3id.org/sirius/agent/")
EVENT = Namespace("https://w3id.org/sirius/event/")

# Load input TTL
g = Graph()
g.parse(INPUT, format="turtle")

# Collect SKOS Concepts
concepts = set(g.subjects(RDF.type, SKOS.Concept))

# Determine leaves (no skos:narrower) and non-leaves (has skos:narrower)
leaves, non_leaves = set(), set()
for c in concepts:
    if any(g.objects(c, SKOS.narrower)):
        non_leaves.add(c)
    else:
        leaves.add(c)

# Helper to create new URIs
def rebase(uri: URIRef, ns: Namespace) -> URIRef:
    local = uri.split("#")[-1].split("/")[-1]
    return ns[local]

# Build URI mapping
mapping = {}

# Non-leaf → agent
for c in non_leaves:
    mapping[c] = rebase(c, AGENT)

# Leaf → event
for c in leaves:
    mapping[c] = rebase(c, EVENT)

# ConceptSchemes → agent
schemes = set(g.subjects(RDF.type, SKOS.ConceptScheme))
for s in schemes:
    mapping[s] = rebase(s, AGENT)

# Create new graph
g2 = Graph()
g2.bind("agent", AGENT)
g2.bind("event", EVENT)
g2.bind("skos", SKOS)

# Copy triples, applying rebasing where applicable
for s, p, o in g:
    s_new = mapping.get(s, s)
    o_new = mapping.get(o, o)
    g2.add((s_new, p, o_new))

# Write output
g2.serialize(OUTPUT, format="turtle")

print(f"✅ Written updated file: {OUTPUT}")
print(f"Non-leaf (agent:) concepts: {len(non_leaves)}")
print(f"Leaf (event:) concepts: {len(leaves)}")
print(f"ConceptSchemes: {len(schemes)}")
