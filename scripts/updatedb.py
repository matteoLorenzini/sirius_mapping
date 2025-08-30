import psycopg2
import xml.etree.ElementTree as ET

# Database connection parameters
db_params = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'gestione_rischio',
    'user': 'postgres',
    'password': '57123Li15!'
}

# Path to your XML file
xml_path = r'xml\risk_analysis.xml'

# Parse XML
tree = ET.parse(xml_path)
root = tree.getroot()

# Connect to database
conn = psycopg2.connect(**db_params)
cur = conn.cursor()

for ra in root.findall('risk_analysis'):
    ra_id = ra.findtext('risk_analysis_id')
    scale_a = ra.findtext('scale_a_description')
    scale_b = ra.findtext('scale_b_description')
    scale_c = ra.findtext('scale_c_description')
    risk_desc = ra.findtext('risk_description')

    cur.execute("""
    UPDATE public.risk_analysis
    SET scale_a_description = %s,
        scale_b_description = %s,
        scale_c_description = %s,
        risk_description = %s
    WHERE risk_analysis_id = %s
""", (scale_a, scale_b, scale_c, risk_desc, ra_id))

conn.commit()
cur.close()
conn.close()
print("All records updated successfully.")