<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                xmlns:dc="http://purl.org/dc/elements/1.1/"
                xmlns:dcterms="http://purl.org/dc/terms/"
                xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
                version="1.0">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:strip-space elements="*"/>

  <!-- path to SPARQL results file (adjust if needed) -->
  <xsl:param name="sparql-file" select="'../source_data/arco/sparql.xml'"/>

  <!-- simple string-replace template (XSLT 1.0) -->
  <xsl:template name="replace">
    <xsl:param name="text"/>
    <xsl:param name="search"/>
    <xsl:param name="replace"/>
    <xsl:choose>
      <xsl:when test="contains($text, $search)">
        <xsl:value-of select="concat(substring-before($text, $search), $replace)"/>
        <xsl:call-template name="replace">
          <xsl:with-param name="text" select="substring-after($text, $search)"/>
          <xsl:with-param name="search" select="$search"/>
          <xsl:with-param name="replace" select="$replace"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$text"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

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

      <!-- derive identifier value to match SPARQL results -->
      <xsl:variable name="idVal" select="normalize-space(dc:identifier)"/>

      <!-- lookup matching SPARQL 'result' by identifier -->
      <xsl:variable name="sparqlRes" select="document($sparql-file)//result[binding[@name='identifier']/literal = $idVal][1]"/>

      <!-- raw address from SPARQL -->
      <xsl:variable name="rawAddr" select="normalize-space($sparqlRes/binding[@name='addressLabel']/literal)"/>

      <!-- remove (P) occurrences -->
      <xsl:variable name="addrNoP">
        <xsl:call-template name="replace">
          <xsl:with-param name="text" select="$rawAddr"/>
          <xsl:with-param name="search" select="'(P)'"/>
          <xsl:with-param name="replace" select="''"/>
        </xsl:call-template>
      </xsl:variable>

      <!-- remove leading prefix "ITALIA, Emilia-Romagna, RA, " if present -->
      <xsl:variable name="prefix" select="'ITALIA, Emilia-Romagna, RA, '"/>
      <xsl:variable name="addrClean">
        <xsl:choose>
          <xsl:when test="string-length($addrNoP) &gt; 0 and substring(normalize-space($addrNoP),1,string-length($prefix)) = $prefix">
            <xsl:value-of select="normalize-space(substring(normalize-space($addrNoP), string-length($prefix) + 1))"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="normalize-space($addrNoP)"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:variable>

      <!-- coordinates: take cleaned address text (kept for geocoding) -->
      <coordinates>
        <xsl:choose>
          <xsl:when test="$sparqlRes and string-length(normalize-space($addrClean)) &gt; 0">
            <xsl:value-of select="$addrClean"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:text/>
          </xsl:otherwise>
        </xsl:choose>
      </coordinates>

      <!-- address: preserve cleaned textual address (without prefix and (P)) -->
      <address>
        <xsl:choose>
          <xsl:when test="$sparqlRes and string-length(normalize-space($addrClean)) &gt; 0">
            <xsl:value-of select="$addrClean"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:text/>
          </xsl:otherwise>
        </xsl:choose>
      </address>

      <!-- chronology: take from SPARQL binding timeLabel if present -->
      <chronology>
        <xsl:choose>
          <xsl:when test="$sparqlRes and string-length(normalize-space($sparqlRes/binding[@name='timeLabel']/literal)) &gt; 0">
            <xsl:value-of select="normalize-space($sparqlRes/binding[@name='timeLabel']/literal)"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:text/>
          </xsl:otherwise>
        </xsl:choose>
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