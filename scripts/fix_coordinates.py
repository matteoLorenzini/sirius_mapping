import os
import re
from lxml import etree

BASE = os.path.dirname(os.path.abspath(__file__))
XML_PATH = os.path.normpath(os.path.join(BASE, "..", "xml", "ravenna.xml"))
BACKUP_PATH = XML_PATH + ".bak"

FLOAT_PAIR_RE = re.compile(r'^\s*([+-]?\d+(?:\.\d+)?)\s+([+-]?\d+(?:\.\d+)?)\s*$')

def main():
    if not os.path.exists(XML_PATH):
        print("File not found:", XML_PATH); return

    # backup
    if not os.path.exists(BACKUP_PATH):
        os.rename(XML_PATH, BACKUP_PATH)
    else:
        # ensure we don't overwrite existing backup
        import shutil
        shutil.copy2(XML_PATH, BACKUP_PATH)

    parser = etree.XMLParser(remove_blank_text=True, recover=True, encoding="utf-8")
    tree = etree.parse(BACKUP_PATH, parser)
    root = tree.getroot()

    swapped = 0
    for el in root.findall(".//coordinates"):
        txt = (el.text or "").strip()
        m = FLOAT_PAIR_RE.match(txt)
        if m:
            lat, lon = m.group(1), m.group(2)
            # swap -> lon lat
            el.text = f"{lon} {lat}"
            swapped += 1

    tree.write(XML_PATH, pretty_print=True, xml_declaration=True, encoding="utf-8")
    print(f"Done. Swapped {swapped} coordinate elements. Original backed up at {BACKUP_PATH}")

if __name__ == "__main__":
    main()