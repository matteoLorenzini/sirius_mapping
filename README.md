# SIRIUS Mapping – Cultural Heritage Risk Management

Utilities to extract data from PostgreSQL to XML, build SKOS thesauri, and produce RDF aligned to CIDOC-CRM.

## Repository structure

```text
sirius_mapping/
├── scripts/
│   ├── sql2xml.py                 # PostgreSQL → XML exporter (outputs to ../xml)
│   ├── iccd_skos.py               # Build SKOS from ICCD Excel (optional)
│   └── updatedb.py                # Example: update DB fields from XML (optional)
├── xml/                           # Generated XML (created at repo root)
│   ├── cultural_heritage_site.xml
│   ├── event_name_sentence.xml
│   ├── risk_analysis.xml          # includes risk_agent and event_name_id
│   ├── value_agents_occurrence.xml
│   └── value_aspect_dimension.xml
├── SKOS/
│   ├── nomenclatura_eventi.csv
│   ├── thesaurus_agenti_eventi.ttl
│   ├── enhanced_full_thesaurus.ttl
│   └── update_skos_from_csv.py    # Rebuild SKOS from CSV (encoding-safe)
├── RDF/
│   ├── E18_site.rdf
│   ├── E89_nara.rdf
│   └── E89_risk_analysis.rdf
├── mapping_3M/
│   ├── E18_site/
│   ├── E89_nara/
│   └── E89_risk/
├── LICENSE
└── README.md
```

## What’s new
- XML outputs now always go to repo_root/xml (one level up from scripts).
- agent_risk_sentence removed; new event_name_sentence.xml added.
- risk_analysis.xml exports both risk_id + risk_agent and the new event_name_id.
- SKOS can be rebuilt from SKOS/nomenclatura_eventi.csv via update_skos_from_csv.py (handles encodings and delimiters).

## Setup (Windows)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install psycopg2-binary rdflib pandas
```

## Export XML from PostgreSQL

Configure DB in scripts/sql2xml.py (host, database, user, password).

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

Notes:
- risk_analysis.xml includes: risk_analysis_id, risk_id, risk_agent, site_id, event_name_id, scale_*_description, risk_description, scores/inputs, uncertainty.

## Update SKOS thesaurus from CSV

Build SKOS/SKOS/enhanced_full_thesaurus.ttl from SKOS/nomenclatura_eventi.csv:
```powershell
python .\SKOS\update_skos_from_csv.py
```
Features:
- Auto-detects encoding (utf-8-sig, utf-8, cp1252, latin-1) and delimiter (; | , tab).
- Supports common headers for IDs, labels, broader links, definitions, alt labels.
- Writes Turtle to SKOS/enhanced_full_thesaurus.ttl.

## Optional: Build SKOS from ICCD Excel

If using the Excel-based builder:
```powershell
python .\scripts\iccd_skos.py
```
- Reads ICCD workbook (row 1 as header; columns A..F as 6 hierarchy levels).
- Filters “BENI IMMOBILI” as root and generates a SKOS hierarchy.

## Troubleshooting

- relation “schema.table” does not exist:
  - Verify schema/table names; use public.risk_analysis or set search_path.
- XML saved to the wrong folder:
  - sql2xml.py creates repo_root/xml and always writes there.
- CSV UnicodeDecodeError:
  - update_skos_from_csv.py auto-detects encoding and normalizes NBSP.
- SKOS hierarchy looks unordered in RDF/XML:
  - RDF is graph-based; use Turtle or a SKOS browser (Protégé, SKOS Play!) to inspect hierarchy.

## License
GNU GPL v3. See LICENSE.