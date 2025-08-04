import psycopg2
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

import os

# Create the xml folder if it doesn't exist
os.makedirs("xml", exist_ok=True)

# Function to prettify XML output
def prettify_xml(elem):
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

# --- 1. Connect to PostgreSQL ---
conn = psycopg2.connect(
    host="localhost",
    database="gestione_rischio",
    user="postgres",
    password="57123Li15!"
)
cursor = conn.cursor()


# --- 2. value_aspect_dimension ---
cursor.execute("""
SELECT 
    vad.value_aspect_dimension_id,
    vad.site_id,
    chs.cultural_heritage_site_appellation AS site,
    vad.aspect_id,
    asp.aspect_appellation AS aspect,
    vad.dimension_id,
    dim.dimension_appellation AS dimension,
    vad.value
FROM public.value_aspect_dimension vad
JOIN public.cultural_heritage_site chs ON vad.site_id = chs.site_id
JOIN public.aspect asp ON vad.aspect_id = asp.aspect_id
JOIN public.dimension dim ON vad.dimension_id = dim.dimension_id
ORDER BY vad.value_aspect_dimension_id;

""")
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]

root = ET.Element("value_aspect_dimensions")
for row in rows:
    item = ET.SubElement(root, "value_aspect_dimension")
    for col_name, col_value in zip(columns, row):
        ET.SubElement(item, col_name).text = str(col_value)
with open("xml/value_aspect_dimension.xml", "w", encoding="utf-8") as f:
    f.write(prettify_xml(root))


# --- 3. cultural_heritage_site ---
cursor.execute("SELECT * FROM public.cultural_heritage_site ORDER BY site_id;")
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]

root = ET.Element("cultural_heritage_sites")
for row in rows:
    item = ET.SubElement(root, "cultural_heritage_site")
    for col_name, col_value in zip(columns, row):
        ET.SubElement(item, col_name).text = str(col_value)
with open("xml/cultural_heritage_site.xml", "w", encoding="utf-8") as f:
    f.write(prettify_xml(root))


# --- 4. value_agents_occurrence ---
cursor.execute("""
SELECT 
    vao.value_agent_occurrence_id,
    vao.risk_id,
    ra.risk_agent,
    vao.occurrence_id,
    ro.occurrence,
    vao.site_id,
    chs.cultural_heritage_site_appellation AS site,
    vao.value_agent_occurrence
FROM public.value_agents_occurrence vao
JOIN public.risk_agents ra ON vao.risk_id = ra.risk_id
JOIN public.risk_occurrence ro ON vao.occurrence_id = ro.occurrence_id
JOIN public.cultural_heritage_site chs ON vao.site_id = chs.site_id
ORDER BY vao.value_agent_occurrence_id;
""")
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]

root = ET.Element("value_agents_occurrences")
for row in rows:
    item = ET.SubElement(root, "value_agents_occurrence")
    for col_name, col_value in zip(columns, row):
        ET.SubElement(item, col_name).text = str(col_value)
with open("xml/value_agents_occurrence.xml", "w", encoding="utf-8") as f:
    f.write(prettify_xml(root))


# --- 5. agent_risk_sentence ---
cursor.execute("""
SELECT 
    ars.agent_risk_sentence_id,
    ars.agent_id,
    ra.risk_agent AS agent,
    ars.site_id,
    chs.cultural_heritage_site_appellation AS site,
    ars.sentence_number,
    ars.sentence_text
FROM public.agent_risk_sentence ars
JOIN public.risk_agents ra ON ars.agent_id = ra.risk_id
JOIN public.cultural_heritage_site chs ON ars.site_id = chs.site_id
ORDER BY ars.agent_risk_sentence_id;
""")
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]

root = ET.Element("agent_risk_sentences")
for row in rows:
    item = ET.SubElement(root, "agent_risk_sentence")
    for col_name, col_value in zip(columns, row):
        ET.SubElement(item, col_name).text = str(col_value)
with open("xml/agent_risk_sentence.xml", "w", encoding="utf-8") as f:
    f.write(prettify_xml(root))


# --- 6. risk_analysis ---
cursor.execute("""
SELECT 
    ra.risk_analysis_id,
    ra.risk_name,
    ra.risk_id,
    r.risk_agent,
    ra.site_id,
    chs.cultural_heritage_site_appellation AS site,
    ars.sentence_text,
    ra.scale_a_score, ra.scale_b_score, ra.scale_c_score,
    ra.magnitude_score, ra.uncertainty
FROM public.risk_analysis ra
JOIN public.risk_agents r ON ra.risk_id = r.risk_id
LEFT JOIN public.agent_risk_sentence ars ON ra.agent_risk_sentence_id = ars.agent_risk_sentence_id
JOIN public.cultural_heritage_site chs ON ra.site_id = chs.site_id
ORDER BY ra.risk_analysis_id;
""")
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]

root = ET.Element("risk_analyses")
for row in rows:
    item = ET.SubElement(root, "risk_analysis")
    for col_name, col_value in zip(columns, row):
        ET.SubElement(item, col_name).text = str(col_value)
with open("xml/risk_analysis.xml", "w", encoding="utf-8") as f:
    f.write(prettify_xml(root))


# --- 7. Done ---
cursor.close()
conn.close()
print("✅ XML files created for:")
print("- value_aspect_dimension")
print("- cultural_heritage_site")
print("- value_agents_occurrence")
print("- agent_risk_sentence")
print("- risk_analysis")
