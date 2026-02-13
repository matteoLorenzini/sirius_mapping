# SIRIUS Mapping – Cultural Heritage Risk Management

Utilities to extract data from PostgreSQL to XML, build SKOS thesauri, transform RDF→XML, and enrich XML with SPARQL/Geocoding data.

## Repository structure

```text
sirius_mapping/
├── scripts/
│   ├── sql2xml.py                 # PostgreSQL → XML exporter (outputs to ../xml)
│   ├── iccd_skos.py               # Build SKOS from ICCD Excel (optional)
│   ├── updatedb.py                # Example: update DB fields from XML (optional)
│   ├── rdf2chs.xsl                # RDF → cultural_heritage_site XML mapping (XSLT)
│   ├── apply_rdf2chs.py           # Run XSLT on RDF (if present)
│   ├── geocode_addresses.py       # Geocode <address> → <coordinates>
│   └── fix_coordinates.py         # Swap lat/lon if needed
├── xml/                           # Generated/processed XML
│   ├── cultural_heritage_site.xml
│   ├── event_name_sentence.xml
│   ├── risk_analysis.xml          # includes risk_agent and event_name_id
│   ├── value_agents_occurrence.xml
│   ├── value_aspect_dimension.xml
│   ├── place.xml                  # place reference data (optional)
│   └── ravenna.xml                # RDF → XML output for Ravenna
├── source_data/
│   └── arco/
│       └── sparql.xml             # SPARQL results (address, time, use, agency)
├── SKOS/
│   ├── nomenclatura_eventi.csv
│   ├── thesaurus_agenti_eventi.ttl
│   ├── enhanced_full_thesaurus.ttl
│   └── update_skos_from_csv.py    # Rebuild SKOS from CSV (encoding-safe)
├── RDF/
│   ├── E18_site.rdf
│   ├── E89_nara.rdf
│   ├── E89_risk_analysis.rdf
│   └── filtered_ravenna.rdf
├── mapping_3M/
│   ├── E18_site/
│   ├── E89_nara/
│   └── E89_risk/
├── LICENSE
└── README.md
```

## What’s new
- Added RDF→XML transformation with `scripts/rdf2chs.xsl`.
- Added SPARQL enrichment support (`source_data/arco/sparql.xml`).
- Added geocoding script (`scripts/geocode_addresses.py`) and coordinate swap helper (`scripts/fix_coordinates.py`).
- Ravenna output is generated in `xml/ravenna.xml`.

## Setup (Windows)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install psycopg2-binary rdflib pandas lxml requests
```

## Export XML from PostgreSQL

Configure DB in `scripts/sql2xml.py` (host, database, user, password).

Run from repo root or anywhere:
```powershell
python .\scripts\sql2xml.py
```

Outputs written to:
- .\xml\cultural_heritage_site.xml
- .\xml\event_name_sentence.xml
- .\xml\risk_analysis.xml
- .\xml\value_agents_occurrence.xml
- .\xml\value_aspect_dimension.xml

## RDF → XML (Ravenna)

Transform RDF to XML with XSLT:
```powershell
python .\scripts\apply_rdf2chs.py
```

Notes:
- `scripts/rdf2chs.xsl` reads `source_data/arco/sparql.xml` to fill address and chronology.
- Output is written to `xml/ravenna.xml`.

## Geocode addresses

Fill `<coordinates>` using `<address>`:
```powershell
python .\scripts\geocode_addresses.py
```

If lat/lon order is reversed, swap them:
```powershell
python .\scripts\fix_coordinates.py
```

## Update SKOS thesaurus from CSV

Build `SKOS/enhanced_full_thesaurus.ttl` from `SKOS/nomenclatura_eventi.csv`:
```powershell
python .\SKOS\update_skos_from_csv.py
```

Features:
- Auto-detects encoding (utf-8-sig, utf-8, cp1252, latin-1) and delimiter (; | , tab).
- Supports common headers for IDs, labels, broader links, definitions, alt labels.
- Writes Turtle to `SKOS/enhanced_full_thesaurus.ttl`.

## Troubleshooting

- relation “schema.table” does not exist:
  - Verify schema/table names; use public.risk_analysis or set search_path.
- XML saved to the wrong folder:
  - `sql2xml.py` creates repo_root/xml and always writes there.
- CSV UnicodeDecodeError:
  - `update_skos_from_csv.py` auto-detects encoding and normalizes NBSP.
- Geocoding misses addresses:
  - Check `scripts/logs/geocode.log` and `scripts/logs/progress.log`.
  - Ensure `<address>` is populated and cleaned.

## License
GNU GPL v3. See LICENSE.