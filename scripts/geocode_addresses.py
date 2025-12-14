import os
import re
import time
import json
import logging
import requests
import urllib.parse
from lxml import etree
from datetime import datetime, timezone

# ========================
# PATHS
# ========================
INPUT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "xml", "ravenna.xml"))
OUTPUT = INPUT
CACHE_FILE = os.path.join(os.path.dirname(__file__), "geocode_cache.json")
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
DEBUG_DIR = os.path.join(LOG_DIR, "debug_nominatim")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DEBUG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "geocode.log")
PROGRESS_FILE = os.path.join(LOG_DIR, "progress.log")
STATUS_FILE = os.path.join(LOG_DIR, "status.json")

# ========================
# LOGGING
# ========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("geocode")

# ========================
# USER AGENT (REQUIRED)
# ========================
USER_EMAIL = os.getenv("USER_EMAIL", "matteo.lorenzini@gmail.com")
USER_AGENT = f"sirius-mapping-geocoder/1.3 ({USER_EMAIL})"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# ========================
# RAVENNA BOUNDING BOX
# ========================
RAVENNA_VIEWBOX = (12.08, 44.33, 12.35, 44.52)  # W, S, E, N

# ========================
# CACHE
# ========================
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        CACHE = json.load(f)
else:
    CACHE = {}

def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(CACHE, f, ensure_ascii=False, indent=2)

# ========================
# HELPERS
# ========================
def looks_like_latlon(s: str) -> bool:
    return bool(re.match(r"^\s*-?\d+(\.\d+)?\s+-?\d+(\.\d+)?\s*$", s or ""))

def is_valid_housenumber(hn: str) -> bool:
    if not hn:
        return False
    hn = hn.strip().lower()
    if hn in {"0", "0a", "snc", "s.n.c.", "s.n.c"}:
        return False
    return True

def strip_house_number(s: str) -> str:
    return re.sub(r"\s+\d+\w*$", "", s or "").strip()

# ========================
# NORMALIZATION
# ========================
ABBREVIATIONS = {
    r"\bS\.?\b": "San",
    r"\bS\.ta\b": "Santa",
    r"\bP\.zza\b": "Piazza",
    r"\bPza\b": "Piazza",
    r"\bC\.so\b": "Corso",
    r"\bV\.le\b": "Viale",
    r"\bV\.?\b": "Via",
}

def normalize_address(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\(P\)", "", s, flags=re.I)
    s = re.sub(r"\bITALIA\b", "Italy", s, flags=re.I)
    s = re.sub(r"\b(s\.?n\.?c\.?)\b", "", s, flags=re.I)

    for k, v in ABBREVIATIONS.items():
        s = re.sub(k, v, s, flags=re.I)

    s = re.sub(r"\s*,\s*", ", ", s)
    s = re.sub(r"\s{2,}", " ", s)
    return s.strip()

STREET_KEYWORDS = [
    "via", "viale", "piazza", "corso", "vicolo", "contrada",
    "strada", "salita", "largo", "piazzale", "borgo"
]

def extract_street_city_housenumber(addr: str):
    parts = [p.strip() for p in addr.split(",") if p.strip()]
    street = None
    housenumber = None
    city = None
    street_idx = None

    for i, p in enumerate(parts):
        if any(k in p.lower() for k in STREET_KEYWORDS):
            street = p
            street_idx = i
            break

    if street:
        m = re.search(r"\b(\d+\w*)\b$", street)
        if m and is_valid_housenumber(m.group(1)):
            housenumber = m.group(1)

    if street_idx is not None and not housenumber and street_idx + 1 < len(parts):
        if re.fullmatch(r"\d+\w*", parts[street_idx + 1]):
            if is_valid_housenumber(parts[street_idx + 1]):
                housenumber = parts[street_idx + 1]

    for i, p in enumerate(parts):
        if i == street_idx:
            continue
        if re.search(r"[A-Za-z]", p):
            city = p
            break

    if not city:
        city = "Ravenna"

    street = strip_house_number(street)

    return street, city, housenumber

# ========================
# DEBUG DUMP
# ========================
def dump_debug(tag, payload):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    fname = os.path.join(DEBUG_DIR, f"{ts}_{tag}.json")
    try:
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# ========================
# NOMINATIM
# ========================
def nominatim_search(params):
    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Language": "it,en"
    }

    w, s, e, n = RAVENNA_VIEWBOX
    base = {
        "format": "jsonv2",
        "limit": 5,
        "viewbox": f"{w},{s},{e},{n}",
        "bounded": 1,
        "addressdetails": 1
    }

    final = {**base, **params}

    try:
        r = requests.get(url, params=final, headers=headers, timeout=20)
        time.sleep(1.0)
        if r.status_code == 200:
            return r.json()
        dump_debug("http_error", {"status": r.status_code, "params": final})
    except requests.RequestException as e:
        dump_debug("exception", {"error": str(e), "params": final})
    return []

def pick_best(results):
    if not results:
        return None
    best = max(results, key=lambda r: float(r.get("importance", 0.0)))
    return best.get("lat"), best.get("lon")

def geocode_nominatim(address: str):
    addr = normalize_address(address)
    street, city, housenumber = extract_street_city_housenumber(addr)

    attempts = []

    if street:
        attempts.append({"street": street, "city": city, "state": "Emilia-Romagna", "country": "Italy"})
        attempts.append({"q": f"{street}, {city}, Emilia-Romagna, Italy"})

    attempts.append({"q": f"{city}, Emilia-Romagna, Italy"})
    attempts.append({"q": f"{addr}, Ravenna, Emilia-Romagna, Italy"})

    for params in attempts:
        logger.info("Nominatim query: %s", params)
        results = nominatim_search(params)
        best = pick_best(results)
        if best:
            return best
        dump_debug("noresult", {"address": address, "params": params, "results": results})

    return None

# ========================
# GOOGLE FALLBACK
# ========================
def geocode_google(address: str):
    if not GOOGLE_API_KEY:
        return None
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_API_KEY}
    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code == 200:
            j = r.json()
            if j.get("status") == "OK":
                loc = j["results"][0]["geometry"]["location"]
                return str(loc["lat"]), str(loc["lng"])
    except requests.RequestException:
        pass
    return None

# ========================
# OVERPASS
# ========================
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_TIMEOUT = 180

def build_overpass_query(street, housenumber, city, bbox=None):
    # match nodes/ways/relations with addr:street and addr:housenumber
    # escape regex chars in street
    s = street.replace('"', '\\"')
    hn_clause = f'["addr:housenumber"="{housenumber}"]' if housenumber else ''
    bbox_clause = f"({bbox[1]},{bbox[0]},{bbox[3]},{bbox[2]})" if bbox else ""
    q = (
        '[out:json][timeout:%d];'
        '('
        f'node["addr:street"~"{s}",i]{hn_clause}{bbox_clause};'
        f'way["addr:street"~"{s}",i]{hn_clause}{bbox_clause};'
        f'relation["addr:street"~"{s}",i]{hn_clause}{bbox_clause};'
        ');out center 1;'
    ) % OVERPASS_TIMEOUT
    return q

def overpass_search(street, housenumber, city, bbox=None, max_attempts=2):
    q = build_overpass_query(street, housenumber, city, bbox)
    params = {"data": q}
    headers = {"User-Agent": USER_AGENT}
    backoff = 1.0
    for attempt in range(max_attempts):
        try:
            r = requests.post(OVERPASS_URL, data=params, headers=headers, timeout=OVERPASS_TIMEOUT)
            if r.status_code == 200:
                j = r.json()
                elements = j.get("elements", [])
                if not elements:
                    return None
                # pick element with most tags / nearest to housenumber if possible
                def score(el):
                    tags = el.get("tags") or {}
                    score = len(tags)
                    # exact housenumber match boosts score
                    if tags.get("addr:housenumber") and housenumber and tags.get("addr:housenumber").lower() == housenumber.lower():
                        score += 100
                    return score
                best = max(elements, key=score)
                lat = best.get("lat") or (best.get("center") or {}).get("lat")
                lon = best.get("lon") or (best.get("center") or {}).get("lon")
                if lat and lon:
                    return str(lat), str(lon)
                return None
            # transient errors: wait and retry
            time.sleep(backoff)
            backoff *= 2
        except requests.RequestException:
            time.sleep(backoff)
            backoff *= 2
    return None

# ========================
# MAIN GEOCODER
# ========================
def geocode(address: str):
    key = address.strip()
    cached = CACHE.get(key)
    if isinstance(cached, dict) and cached.get("ok"):
        return cached["lat"], cached["lon"]

    # parse address components
    addr_norm = normalize_address(key)
    street, city, housenumber = extract_street_city_housenumber(addr_norm)

    # 1) try Overpass (OSM addr:* tags)
    if street:
        logger.info("Trying Overpass for: street=%s housenumber=%s city=%s", street, housenumber, city)
        ov = overpass_search(street, housenumber, city, bbox=RAVENNA_VIEWBOX)
        if ov:
            CACHE[key] = {"ok": True, "lat": ov[0], "lon": ov[1], "source": "overpass"}
            save_cache()
            return ov

    # 2) fall back to previous Nominatim-based routine
    res = geocode_nominatim(key)
    if res:
        CACHE[key] = {"ok": True, "lat": res[0], "lon": res[1], "source": "nominatim"}
        save_cache()
        return res

    # 3) optional Google
    g = geocode_google(key)
    if g:
        CACHE[key] = {"ok": True, "lat": g[0], "lon": g[1], "source": "google"}
        save_cache()
        return g

    # failure
    CACHE[key] = {"ok": False, "ts": datetime.now(timezone.utc).isoformat()}
    save_cache()
    return None

# ========================
# XML LOOP
# ========================
def write_progress_line(resource_id, idx, total, addr, success, source=None, message=None):
    ts = datetime.now(timezone.utc).isoformat()
    line = {
        "ts": ts,
        "resource": resource_id,
        "index": idx,
        "total": total,
        "address": addr,
        "success": bool(success),
        "source": source,
        "message": message
    }
    try:
        with open(PROGRESS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
    except Exception:
        logger.debug("Failed to write progress line")

def write_status(total, processed, updated, last_resource, last_address, last_success, last_source):
    status = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total": total,
        "processed": processed,
        "updated": updated,
        "last": {
            "resource": last_resource,
            "address": last_address,
            "success": bool(last_success),
            "source": last_source
        }
    }
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(status, f, ensure_ascii=False, indent=2)
    except Exception:
        logger.debug("Failed to write status file")

def main():
    tree = etree.parse(INPUT, etree.XMLParser(recover=True))
    root = tree.getroot()

    total = 0
    updated = 0
    processed = 0

    sites = root.findall(".//cultural_heritage_site")
    total = len(sites)
    logger.info("Found %d cultural_heritage_site elements", total)
    # initialize status
    write_status(total, processed, updated, None, None, False, None)

    for idx, site in enumerate(sites, start=1):
        addr_el = site.find("address")
        coord_el = site.find("coordinates")

        # Get text from the address tag (might be empty)
        addr_from_tag = (addr_el.text or "").strip() if addr_el is not None else ""
        
        # Get text from the coordinates tag (this holds the raw address OR the lat/lon)
        coord_text = (coord_el.text or "").strip() if coord_el is not None else ""

        # --- CRITICAL FIX START ---
        # If the standard <address> is empty, use the text from <coordinates> 
        # as the address to be geocoded, as specified by the user's intent.
        addr = addr_from_tag if addr_from_tag else coord_text
        # --- CRITICAL FIX END ---

        # The coordinate value (for existing data check) is still coord_text
        coord = coord_text

        # derive resource id for logging
        codice_el = site.find("codice_catalogo_nazionale")
        siteid_el = site.find("site_id")
        codice = (codice_el.text or "").strip() if codice_el is not None else ""
        siteid = (siteid_el.text or "").strip() if siteid_el is not None else ""
        resource_id = codice or siteid or addr or f"idx-{idx}"

        # log start
        logger.info("Processing [%d/%d] %s", idx, total, resource_id)
        processed += 1

        if looks_like_latlon(coord):
            logger.info("Skipping %s: coordinates already in lat/lon (%s)", resource_id, coord)
            write_progress_line(resource_id, idx, total, addr, True, None, "already-latlon")
            write_status(total, processed, updated, resource_id, addr, True, None)
            continue

        if not addr:
            logger.info("Skipping %s: no address", resource_id)
            write_progress_line(resource_id, idx, total, addr, False, None, "no-address")
            write_status(total, processed, updated, resource_id, addr, False, None)
            continue

        logger.info("Geocoding [%d/%d] %s — %s", idx, total, resource_id, addr)
        # We pass the cleaned 'addr' (which contains the address string) to geocode()
        geo = geocode(addr)

        if geo:
            lat, lon = geo
            if coord_el is None:
                # If <coordinates> tag didn't exist, create it
                coord_el = etree.SubElement(site, "coordinates")
            
            # Update the <coordinates> element with the lat/lon
            coord_el.text = f"{lat} {lon}"
            updated += 1
            logger.info("Geocoded %s -> %s %s", resource_id, lat, lon)
            # attempt to capture source from cache if available
            cached = CACHE.get(addr)
            src = None
            if isinstance(cached, dict):
                src = cached.get("source")
            write_progress_line(resource_id, idx, total, addr, True, src, None)
            write_status(total, processed, updated, resource_id, addr, True, src)
        else:
            logger.warning("FAILED to geocode %s — %s", resource_id, addr)
            write_progress_line(resource_id, idx, total, addr, False, None, "not-found")
            write_status(total, processed, updated, resource_id, addr, False, None)

    if updated:
        tree.write(OUTPUT, pretty_print=True, xml_declaration=True, encoding="utf-8")

    logger.info("DONE. Total=%d Processed=%d Updated=%d", total, processed, updated)
    # final status write
    write_status(total, processed, updated, None, None, False, None)

if __name__ == "__main__":
    main()