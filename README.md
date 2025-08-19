# SIRIUS Mapping - Cultural Heritage Risk Management System

A comprehensive data transformation and semantic mapping toolkit for cultural heritage risk management, featuring PostgreSQL-to-XML conversion and CIDOC-CRM RDF mapping capabilities.
The system bridges the gap between traditional relational database storage and semantic web technologies, enabling:

- **Risk Assessment Documentation**: Comprehensive tracking of risks affecting cultural heritage sites
- **Semantic Interoperability**: CIDOC-CRM compliant RDF mappings for cultural heritage data
- **Data Integration**: Standardized XML exports for cross-platform compatibility
- **Heritage Management**: Structured approach to cultural site preservation and risk mitigation

## 📁 Repository Structure

```text
sirius_mapping/
├── scripts/
│   ├── sql2xml.py              # PostgreSQL to XML conversion tool
│   └── xml/                    # Generated XML exports
│       ├── agent_risk_sentence.xml
│       ├── cultural_heritage_site.xml
│       ├── risk_analysis.xml
│       ├── value_agents_occurrence.xml
│       └── value_aspect_dimension.xml
├── mapping_3M/
│   ├── E18_site/              # CIDOC-CRM E18 Physical Thing mappings
│   ├── E89_nara/              # NARA (National Archives) mappings
│   └── E89_risk/              # Risk assessment mappings
├── RDF/
│   ├── E18_site.rdf           # Cultural heritage sites RDF
│   ├── E89_nara.rdf           # NARA compliance RDF
│   └── E89_risk_analysis.rdf  # Risk analysis RDF
├── LICENSE                    # GNU GPL v3 License
└── README.md                  # This file
```

## 🔧 Core Components

### 1. Database Export Tool (`scripts/sql2xml.py`)

A Python script that extracts data from a PostgreSQL database (`gestione_rischio`) and converts it to structured XML format. The tool processes:

- **Cultural Heritage Sites**: Complete site information and metadata
- **Risk Analysis**: Comprehensive risk assessments with scoring systems
- **Value-Aspect Dimensions**: Site valuations across multiple criteria
- **Agent Risk Sentences**: Detailed risk descriptions and documentation
- **Value Agent Occurrences**: Risk occurrence tracking and relationships

**Key Features:**

- Preserves both numerical IDs and human-readable labels
- Maintains referential integrity through foreign key relationships
- Generates well-formatted XML with proper encoding (UTF-8)
- Includes comprehensive JOIN operations for complete data context

### 2. CIDOC-CRM Mappings (`mapping_3M/` & `RDF/`)

Semantic mappings following the [CIDOC Conceptual Reference Model](http://www.cidoc-crm.org/) standard:

- **E18_Physical_Thing**: Cultural heritage sites and physical objects
- **E89_Propositional_Object**: Risk assessments and analytical propositions
- **NARA Integration**: National Archives compliance mappings

### 3. RDF Output

Semantic web-ready RDF files that provide:

- CIDOC-CRM compliant cultural heritage descriptions
- Linked data capabilities for heritage information systems
- Standardized vocabularies using SKOS and OWL

## 🛠️ Technical Requirements

- **Python 3.x** with libraries:
  - `psycopg2` (PostgreSQL adapter)
  - `xml.etree.ElementTree` (XML processing)
  - `xml.dom.minidom` (XML formatting)
- **PostgreSQL** database with `gestione_rischio` schema
- **RDF processing tools** (for semantic data handling)

## 🚀 Usage

### Database Export

1. Ensure PostgreSQL database `gestione_rischio` is accessible
2. Configure database connection parameters in `sql2xml.py`
3. Run the export script:

```bash
cd scripts
python sql2xml.py
```

Generated XML files will be saved in the `scripts/xml/` directory.

### Data Structure

The system processes five main entity types:

1. **Cultural Heritage Sites** - Physical locations and their properties
2. **Risk Analysis** - Quantitative and qualitative risk assessments
3. **Value Aspect Dimensions** - Multi-dimensional site valuations
4. **Agent Risk Sentences** - Textual risk descriptions
5. **Value Agent Occurrences** - Risk event tracking

Each export includes both numerical identifiers and descriptive labels for maximum data utility.

## 🎯 Use Cases

- **Heritage Conservation**: Risk-based prioritization of conservation efforts
- **Policy Making**: Data-driven cultural heritage protection policies
- **Academic Research**: Standardized datasets for heritage studies
- **Digital Humanities**: Semantic web integration for cultural data
- **Risk Management**: Systematic approach to heritage site preservation

## 📊 Data Model

The system implements a comprehensive relational model covering:

- Site identification and classification
- Multi-dimensional risk assessment (scales A, B, C)
- Uncertainty quantification
- Temporal risk tracking
- Stakeholder and administrative context
- Value attribution across multiple aspects and dimensions