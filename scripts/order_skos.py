#!/usr/bin/env python3
# fix_double_underscores.py
# Post-process an RDF/XML (or Turtle) file produced earlier:
#  - replace non-breaking spaces (U+00A0) inside URIRefs with underscore
#  - collapse runs of multiple underscores into a single underscore
#  - keep percent-encoding for non-ASCII characters already present

import re
from rdflib import Graph, URIRef
from urllib.parse import unquote, quote
import sys

NBSP = "\u00A0"

def normalize_uri_str(s):
    # operate on string: replace NBSP with underscore, collapse underscores, preserve other chars
    s2 = s.replace(NBSP, "_")
    # collapse multiple underscores into single
    s2 = re.sub(r"_+", "_", s2)
    # We want non-ASCII characters percent-encoded (utf-8)
    # Split by scheme+authority to avoid encoding colon and slashes
    # naive approach: encode everything except reserved URI chars
    safe = ":/?#[]@!$&'()*+,;=%_"
    return quote(s2, safe=safe)

def process_file(infile, outfile):
    g = Graph()
    fmt = "xml"
    try:
        g.parse(infile, format=fmt)
    except Exception as e:
        # try turtle as fallback
        try:
            g.parse(infile, format="turtle")
            fmt = "turtle"
        except Exception:
            raise SystemExit(f"Failed to parse {infile} as RDF/XML or Turtle: {e}")

    g2 = Graph()
    for prefix, ns in g.namespaces():
        if prefix:
            g2.bind(prefix, ns)
    for s, p, o in g:
        s2 = s
        p2 = p
        o2 = o
        if isinstance(s, URIRef):
            s2 = URIRef(normalize_uri_str(str(s)))
        if isinstance(p, URIRef):
            p2 = URIRef(normalize_uri_str(str(p)))
        if isinstance(o, URIRef):
            o2 = URIRef(normalize_uri_str(str(o)))
        g2.add((s2, p2, o2))

    # Serialize as RDF/XML (fallback to turtle on failure)
    try:
        g2.serialize(destination=outfile, format="xml", encoding="utf-8")
        print("Wrote fixed RDF/XML to", outfile)
    except Exception as e:
        out2 = outfile.rsplit(".", 1)[0] + ".ttl"
        g2.serialize(destination=out2, format="turtle", encoding="utf-8")
        print("RDF/XML serialization failed; wrote Turtle to", out2, ". Error:", e)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fix_double_underscores.py in.rdf out.rdf")
        sys.exit(1)
    process_file(sys.argv[1], sys.argv[2])
