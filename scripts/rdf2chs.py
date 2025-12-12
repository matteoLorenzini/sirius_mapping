# Apply XSLT to RDF/XML and write cultural_heritage_site.xml
import os
from lxml import etree

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(BASE_DIR, ".."))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "xml")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Input RDF/XML (adjust path as needed)
RDF_INPUT = os.path.normpath(os.path.join(PROJECT_ROOT, "RDF", "filtered_ravenna.rdf"))
XSLT_PATH = os.path.join(BASE_DIR, "rdf2chs.xsl")
OUTPUT_XML = os.path.join(OUTPUT_DIR, "ravenna.xml")

def transform(rdf_input, xslt_path, out_path):
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding="utf-8")
    rdf_doc = etree.parse(rdf_input, parser)
    xslt_doc = etree.parse(xslt_path, parser)
    transform = etree.XSLT(xslt_doc)
    result = transform(rdf_doc)
    # pretty print and write
    with open(out_path, "wb") as f:
        f.write(etree.tostring(result, pretty_print=True, xml_declaration=True, encoding="utf-8"))
    print("Wrote:", out_path)

if __name__ == "__main__":
    transform(RDF_INPUT, XSLT_PATH, OUTPUT_XML)