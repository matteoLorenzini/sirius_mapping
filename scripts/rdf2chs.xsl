<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                xmlns:dc="http://purl.org/dc/elements/1.1/"
                xmlns:dcterms="http://purl.org/dc/terms/"
                xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
                version="1.0">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <!-- Root -->
  <xsl:template match="/">
    <cultural_heritage_sites>
      <xsl:apply-templates select="//rdf:Description[dc:identifier]"/>
    </cultural_heritage_sites>
  </xsl:template>

  <!-- Each RDF description becomes a cultural_heritage_site -->
  <xsl:template match="rdf:Description[dc:identifier]">
    <cultural_heritage_site>
      <!-- site_id: sequential per output (position in this for-each) -->
      <site_id>
        <xsl:number count="rdf:Description[dc:identifier]" level="any"/>
      </site_id>

      <!-- appellation: first literal dc:subject (ignore dc:subject with rdf:resource attr) -->
      <cultural_heritage_site_appellation>
        <xsl:value-of select="dc:subject[not(@rdf:resource)][1]"/>
      </cultural_heritage_site_appellation>

      <!-- typology: take the value directly from dc:type -->
      <typology>
        <xsl:value-of select="normalize-space(dc:type)"/>
      </typology>

      <!-- coordinates: not present in RDF snippet -> leave empty (or map if you have a predicate) -->
      <coordinates>
        <xsl:text/>
      </coordinates>

      <!-- chronology: leave empty for now -->
      <chronology>
        <xsl:text/>
      </chronology>

      <!-- description: try rdfs:comment, else empty -->
      <description>
        <xsl:choose>
          <xsl:when test="string-length(normalize-space(rdfs:comment)) &gt; 0">
            <xsl:value-of select="normalize-space(rdfs:comment)"/>
          </xsl:when>
          <xsl:otherwise/>
        </xsl:choose>
      </description>

      <!-- socio-cultural_context: leave empty -->
      <socio-cultural_context>
        <xsl:text/>
      </socio-cultural_context>

      <!-- administrative_context: map from dc:rights -->
      <administrative_context>
        <xsl:choose>
          <xsl:when test="string-length(normalize-space(dc:rights)) &gt; 0">
            <xsl:value-of select="normalize-space(dc:rights)"/>
          </xsl:when>
          <xsl:otherwise/>
        </xsl:choose>
      </administrative_context>

      <!-- financial_context: leave empty for now -->
      <financial_context>
        <xsl:text/>
      </financial_context>

      <!-- legal_context: leave empty for now -->
      <legal_context>
        <xsl:text/>
      </legal_context>

      <!-- stakeholders: leave empty for now -->
      <stakeholders>
        <xsl:text/>
      </stakeholders>

      <!-- place_id: map dc:coverage text to place id (example Ravenna (RA) -> 2) -->
      <place_id>
        <xsl:choose>
          <xsl:when test="normalize-space(dc:coverage) = 'Ravenna (RA)'">2</xsl:when>
          <xsl:otherwise/>
        </xsl:choose>
      </place_id>

      <!-- codice_catalogo_nazionale from dc:identifier -->
      <codice_catalogo_nazionale>
        <xsl:value-of select="normalize-space(dc:identifier)"/>
      </codice_catalogo_nazionale>
    </cultural_heritage_site>
  </xsl:template>
</xsl:stylesheet>