"""
Scraper for gnfchem.com — uses sitemap URLs, saves to scrape_output.json.
Run: python scrape_gnfchem.py
"""
import json
import re
import time

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"}

# Skip these categories (pharmaceutical / non-food-additive)
SKIP_CATEGORIES = {"api", "API"}

CATEGORY_MAP = {
    "Sweeteners": "Sweeteners",
    "Thickeners": "Thickeners",
    "Vitamins": "Vitamins",
    "Preservatives": "Preservatives",
    "Proteins": "Proteins",
    "Acidulants": "Acidulants",
    "Amino Acids": "Amino Acids",
    "Antioxidants": "Antioxidants",
    "Cocoa Series": "Cocoa Series",
    "Dehydrated Vegetables": "Dehydrated Vegetables",
    "Emulsifiers": "Emulsifiers",
    "Flavorings": "Flavorings",
    "Phosphates": "Phosphates",
    "Plant Extracts": "Plant Extracts",
    "Enzyme": "Enzymes",
    "Nutritional Supplement": "Nutritional Supplements",
    "Surfactant": "Surfactants",
    "Others": "Others",
}

PRODUCT_URLS = [
    "https://www.gnfchem.com/food-grade-acidulants-trisodium-citrate-cas-6132-04-3",
    "https://www.gnfchem.com/food-additives-acidulants-dl-tartaric-acid-white-granule-powder-cas-133-37-9",
    "https://www.gnfchem.com/food-additives-acidulants-acetic-acid-cas-64-19-7",
    "https://www.gnfchem.com/food-industry-food-acidulant-lactic-acid-yellow-liquid-cas-50-21-5",
    "https://www.gnfchem.com/food-additives-acidulants-dl-malic-acid-white-crystalline-granule-powder-cas-617-48-16915-15-7",
    "https://www.gnfchem.com/food-additives-acidulants-food-grade-potassium-citrate-cas-866-84-2",
    "https://www.gnfchem.com/food-additives-acidulants-fumaric-acid-white-powder-cas-110-17-8",
    "https://www.gnfchem.com/food-additives-grade-acidifiers-flavoring-agents-citric-acid-cas-5949-29-1",
    "https://www.gnfchem.com/amino-acids-food-grade-amino-acids-creatine-mono-powder-cas-6020-87-7",
    "https://www.gnfchem.com/nutritional-supplements-weight-loss-white-powder-acetyl-l-carnitine-hcl-cas-5080-50-2",
    "https://www.gnfchem.com/white-powder-amino-acids-skin-whitening-cosmetic-grade-theanine-cas-3081-61-6",
    "https://www.gnfchem.com/nutritional-supplement-food-grade-glucosamine-chondroitin-sulfate-cas-29031-19-4",
    "https://www.gnfchem.com/food-additives-nutritional-supplement-water-soluble-l-carnitine-tartrate-cas-541-15-1",
    "https://www.gnfchem.com/food-addition-amino-acids-l-valine-white-powder-cas-72-18-4",
    "https://www.gnfchem.com/light-yellow-feed-grade-amino-acids-feed-grade-l-threonine-985-feed-grade-cas-72-19-5",
    "https://www.gnfchem.com/amino-acids-feed-grade-amino-acids-light-gray-crystal-dl-methioninefeed-grade-cas-59-51-8",
    "https://www.gnfchem.com/powder-l-carnitine-fumarate-food-grade-l-carnitine-fumarate-cas-90471-79-7",
    "https://www.gnfchem.com/nutritional-supplements-food-additives-methyl-sulfonyl-methane-msm-cas-67-71-0",
    "https://www.gnfchem.com/food-grade-healthy-nourishment-nutrition-l-glutamine-powder-cas-56-85-9",
    "https://www.gnfchem.com/lipid-metabolism-food-supplement-nutritional-supplements-l-carnitine-cas-541-15-1",
    "https://www.gnfchem.com/nutrient-enhancer-supplement-nutritional-taurine-cas-107-35-7",
    "https://www.gnfchem.com/antioxidants-preservative-sodium-methyl-paraben-cas-5026-62-0",
    "https://www.gnfchem.com/antioxidant-food-additives-cocoa-series-alkalized-coco-powder",
    "https://www.gnfchem.com/cocoa-series-ingredients-food-additives-natural-coco-powder",
    "https://www.gnfchem.com/food-additives-ethanolamine-powder-cas-141-43-5",
    "https://www.gnfchem.com/pharmaceutical-grade-tarquinor-food-additives-halquinol-cas-8067-69-4",
    # skip: api-raw-materials-ibuprofen (pharmaceutical)
    "https://www.gnfchem.com/food-additives-enzymetransglutaminase-tx10-cas-80146-85-6",
    "https://www.gnfchem.com/food-additives-enzymatic-preparation-transglutaminase-tx06-cas-80146-85-6",
    "https://www.gnfchem.com/food-grade-additives-enzyme-v-nicotinamide-mononucleotidegrade-i-cas-1094-61-7",
    "https://www.gnfchem.com/food-grade-antioxidants-preservative-propyl-paraben-cas-94-13-3",
    "https://www.gnfchem.com/antioxidants-food-additives-sodium-propyl-paraben-cas-35285-69-9",
    "https://www.gnfchem.com/food-additives-antioxidants-methyl-paraben-cas-99-76-3",
    "https://www.gnfchem.com/pharmaceutical-grade-antioxidants-silicon-dioxide-cas-7631-86-9",
    "https://www.gnfchem.com/antioxidants-food-additives-titanium-dioxiderutileanatase-cas-13463-67-7",
    "https://www.gnfchem.com/antioxidant-sodium-isoascorbate-erythorbic-acid-cas-89-65-6",
    "https://www.gnfchem.com/food-additives-antioxidants-sodium-ascorbate-cas-134-03-2",
    "https://www.gnfchem.com/food-additives-antioxidants-ascorbic-acidvitamin-c-cas-50-81-7",
    "https://www.gnfchem.com/antioxidants-vitamin-c-palmitate-ascorbyl-palmitate-cas-137-66-6",
    "https://www.gnfchem.com/food-grade-antioxidants-isoascorbate-sodium-erythorbate-cas-6381-77-7",
    "https://www.gnfchem.com/food-grade-additives-vegetable-extract-dehydrate-tomato-powder",
    "https://www.gnfchem.com/food-additives-grade-vegetables-dehydrate-onion-powder",
    "https://www.gnfchem.com/food-additives-grade-dehydrate-onion-flakes-haracteristic-flavorintroduction-food-grade",
    "https://www.gnfchem.com/food-additives-kiln-dehydrate-garlic-flakes-food-grade",
    "https://www.gnfchem.com/emulsifiers-enzyme-food-additives-soya-lecithin-liquid-cas-8002-43-5",
    "https://www.gnfchem.com/emulsifiers-food-additives-food-grade-soy-lecithin-powder-cas-8002-43-5",
    "https://www.gnfchem.com/usp-grade-emulsifiers-food-grade-propylene-glycol-cas-57-55-6",
    "https://www.gnfchem.com/usp-food-grade-emulsifiers-food-additives-glycerin-995-cas-56-81-5",
    "https://www.gnfchem.com/distilled-glycerin-monostearatedgm-cas-31566-31-1",
    "https://www.gnfchem.com/food-additives-ethyl-maltol-flavor-enhancers-flavorings-maltol-cas-118-71-8",
    "https://www.gnfchem.com/molasses-yeast-flavorings-food-additives-emulsifier-instant-dry-yeast",
    "https://www.gnfchem.com/flavorings-food-additives-menthol-crystal-white-crystal-cas-89-78-1",
    "https://www.gnfchem.com/sweetener-food-flavor-food-additives-ethyl-maltol-cas-118-71-8",
    "https://www.gnfchem.com/food-additives-food-grade-flavor-enhancers-ethyl-vanillin-cas-121-33-5",
    "https://www.gnfchem.com/flavorings-food-additives-monosodium-glutamate-99-cas-142-47-2",
    "https://www.gnfchem.com/flavor-enhancers-food-additives-grade-vanillin-cas-121-33-5",
    "https://www.gnfchem.com/phosphates-food-additives-feed-grade-sodium-bicarbonate-cas-144-55-8",
    "https://www.gnfchem.com/food-additives-pectin-curing-agent-tricalcium-phosphate-cas-7758-87-4",
    "https://www.gnfchem.com/detergent-food-ingredients-additives-trisodium-phosphate-cas-7601-54-9",
    "https://www.gnfchem.com/food-additives-grade-phosphoric-acid-cas-7664-38-2",
    "https://www.gnfchem.com/blend-compound-food-phosphate-cas-10124-56-8",
    "https://www.gnfchem.com/sodium-hexametaphosphateshmp-cas-10124-56-8",
    "https://www.gnfchem.com/emulsifier-food-grade-additives-sodium-acid-pyrophosphatesapp-cas-7758-16-9",
    "https://www.gnfchem.com/industrial-food-additives-grade-sodium-tripolyphosphate-cas-7758-29-4",
    "https://www.gnfchem.com/organic-food-additives-plant-extracts-moringa-oleifera-leaf-powder",
    "https://www.gnfchem.com/health-organic-food-additives-tribulus-terrestris-extract-cas-90131-68-3",
    "https://www.gnfchem.com/organic-food-additives-ingredients-chlorella-powder",
    "https://www.gnfchem.com/organic-food-grade-ingredients-organic-inulin",
    "https://www.gnfchem.com/plant-extracts-food-grade-additives-glycyrrhizin-acid-licorice-extract-cas-1405-86-3",
    "https://www.gnfchem.com/reagent-grade-industrial-grade-food-additives-grade-edta-4na-cas-13235-36-4",
    "https://www.gnfchem.com/preservatives-food-additives-grade-benzoic-acid-cas-65-85-0",
    "https://www.gnfchem.com/thickening-agent-food-additives-sodium-acetate-anhydrous-cas-4075-81-4",
    "https://www.gnfchem.com/food-additives-grade-antioxidant-glucono-delta-lactonegdl-cas-90-80-2",
    "https://www.gnfchem.com/acidity-regulators-food-additives-grade-sodium-propionate-cas-6132-04-3",
    "https://www.gnfchem.com/food-additives-grade-preservative-sodium-benzoate-cas-532-32-1",
    "https://www.gnfchem.com/food-additives-food-grade-calcium-propionate-cas-4075-81-4",
    "https://www.gnfchem.com/preservatives-food-additives-potassium-sorbate-granular-cas-590-00-1",
    "https://www.gnfchem.com/protein-food-additives-grade-healthy-sorbic-acid-cas-110-44-1",
    "https://www.gnfchem.com/food-preservative-food-grade-additives-natamycin-cas-7681-93-8",
    "https://www.gnfchem.com/food-ingredients-food-additives-food-grade-nisin-cas-1414-45-5",
    "https://www.gnfchem.com/soybean-powder-food-grade-food-additives-pea-fiber",
    "https://www.gnfchem.com/industrial-grade-stabilizer-healthy-textured-soy-protein-cas-9000-10-0",
    "https://www.gnfchem.com/food-additives-food-grade-rice-protein-cas-na",
    "https://www.gnfchem.com/acids-feed-grade-food-additives-hydrolyzed-animal-protein-cas-92113-31-0",
    "https://www.gnfchem.com/food-grade-additives-acidity-regulators-dietary-soy-fiber-cas-9000-70-8",
    "https://www.gnfchem.com/food-additives-grade-organic-pea-protein-cas-90-10-0",
    "https://www.gnfchem.com/health-foods-beverage-grade-organic-hemp-protein",
    "https://www.gnfchem.com/food-additives-grade-proteins-vital-wheat-gluten-cas-8002-80-0",
    "https://www.gnfchem.com/food-additives-food-grade-soy-protein-concentrate-cas-na",
    "https://www.gnfchem.com/food-additives-emulsifiers-grade-protein-isolated-soy-proteinisp-cas-9010-10-0",
    "https://www.gnfchem.com/food-additives-grade-sweeteners-dextrose-monohydrate-cas-5996-10-1",
    "https://www.gnfchem.com/sweeteners-food-industry-food-additives-grade-neotame-cas-165450-17-9",
    "https://www.gnfchem.com/food-additives-grade-sweeteners-erythritol-cas-149-32-6",
    "https://www.gnfchem.com/food-additives-grade-confectionery-crystalline-fructose-cas-57-48-7",
    "https://www.gnfchem.com/food-additives-food-grade-allulosed-allulosed-psicose-cas-551-68-8",
    "https://www.gnfchem.com/sweeteners-dietary-fiber-food-additives-grade-poly-d-glucose-polyglucose-cas-68424-04-4",
    "https://www.gnfchem.com/food-additives-grade-sweeteners-maltitol-75-cas-585-88-6",
    "https://www.gnfchem.com/food-ingredients-food-additives-blending-for-monk-fruit-erythritol-cas-149-32-6",
    "https://www.gnfchem.com/food-additives-food-ingredients-sweeteners-sodium-saccharin-cas-204-886-1",
    "https://www.gnfchem.com/daily-flavor-food-additives-grade-food-industry-xylitol-cas-87-99-0",
    "https://www.gnfchem.com/sweeteners-food-additives-grade-sodium-cyclamate-cas-68476-78-8",
    "https://www.gnfchem.com/food-additives-grade-beverage-grade-acesulfame-k-cas-33665-90-6",
    "https://www.gnfchem.com/beverage-grade-food-additives-confectionery-grade-sucralose-cas-56038-13-2",
    "https://www.gnfchem.com/beverage-grade-food-additives-food-grade-sweeteners-aspartame-cas-22839-47-0",
    "https://www.gnfchem.com/food-grade-additives-emulsifiers-thickeners-xanthan-gum-cas-11138-66-2",
    "https://www.gnfchem.com/food-ingredients-thickeners-citrus-pectin-cas-9000-69-5",
    "https://www.gnfchem.com/absorbent-surfactant-food-additives-grade-sodium-alginate-cas-9005-38-3",
    "https://www.gnfchem.com/food-grade-beverage-grade-gelatinbeefpork-fish-based-cas-9000-70-8",
    "https://www.gnfchem.com/food-additives-grade-thickeners-carrageenan-kappa-refiend-cas-9000-07-1",
    "https://www.gnfchem.com/food-garde-additives-kappa-carrageenan-semi-refined-cas-9000-07-1",
    "https://www.gnfchem.com/food-additives-grade-thickeners-stabilizers-sodium-carboxymethyl-cellulosecmc-cas-9004-32-4",
    "https://www.gnfchem.com/food-additives-grade-thickeners-xanthan-gum-200mesh-cas-11138-66-2",
    "https://www.gnfchem.com/preservatives-food-additives-emulsifiers-nutrient-enhancers-apple-pectin-cas-9000-70-8",
    "https://www.gnfchem.com/healthy-organic-food-additives-grade-stabilizers-agar-agar-cas-9002-18-0",
    "https://www.gnfchem.com/food-additives-grade-stabilizers-thickeners-xanthan-gum-80mesh-cas-11138-66-2",
    "https://www.gnfchem.com/healthy-organic-konjac-gum-cas-37220-17-0",
    "https://www.gnfchem.com/high-dietary-fiber-food-additives-health-food-vitamin-b5-cas-16485-10-2",
    "https://www.gnfchem.com/cosmetic-grade-food-ingredients-food-additives-grade-vitamin-b3-cas-98-92-0",
    "https://www.gnfchem.com/high-dietary-fiber-food-additives-grade-vitamin-b12-cyanocobalamin-cas-68-19-9",
    "https://www.gnfchem.com/healthy-organic-food-additives-grade-inositol-cas-87-89-8",
    "https://www.gnfchem.com/food-additives-grade-nutritional-enhancers-feed-grade-d-biotinvitamin-h-cas-58-85-5",
    "https://www.gnfchem.com/high-dietary-fiber-food-additives-grade-vitamin-e-oil-98-cas-7695-91-2",
    "https://www.gnfchem.com/food-additives-grade-nutritional-enhancers-vitamin-e-powder-cas-58-56-0",
    "https://www.gnfchem.com/acidity-regulators-food-additives-grade-ascorbic-acidvitamin-c-cas-50-81-7",
    "https://www.gnfchem.com/health-food-food-additives-grade-healthy-organic-beta-carotene",
    "https://www.gnfchem.com/food-additives-grade-healthy-organic-energy-metabolism-vitamin-b2-riboflavin",
    "https://www.gnfchem.com/food-grade-food-additives-plant-extracts-exercise-supplement-vitamin-b12-methylcobalamin",
    "https://www.gnfchem.com/food-additives-health-food-food-grade-stabilizers-vitamin-b6-cas-58-56-0",
    "https://www.gnfchem.com/food-additives-grade-animal-feed-feed-grade-vitamin-b1-mononitrate-cas-59-43-8",
    "https://www.gnfchem.com/food-grade-food-additives-food-supplements-health-food-nutritional-enhancers-vitamin-b1-hcl-cas-59-43-8",
    "https://www.gnfchem.com/high-dietary-fiber-food-additives-food-grade-health-food-vitamin-b9folic-acid",
    "https://www.gnfchem.com/food-additives-grade-food-ingredient-maltodextrin-cas-9050-36-6",
    "https://www.gnfchem.com/food-additives-xanthan-gum-oil-drilling-grade-cas-11138-66-2",
    "https://www.gnfchem.com/vitamin-e-feed-grade-antibiotics-and-antimicrobials-immunity-enhancement",
    "https://www.gnfchem.com/sodium-lauryl-ether-sulfate-sles-70-surfactant-supplier-cas68585-34-2",
    "https://www.gnfchem.com/food-additive-essence-and-fragrance-laurel-leaf",
    "https://www.gnfchem.com/food-additive-essence-and-fragrance-gnf-condiment-star-anise",
    "https://www.gnfchem.com/food-additive-high-purity-food-grade-mannitol-sweetener-cas-no69-65-8",
    "https://www.gnfchem.com/hot-selling-wholesale-price-food-additive-sweetener-stevia-extract-cas-no57817-89-7",
    "https://www.gnfchem.com/food-additive-emulsifier-mono-and-diglycerides-of-fatty-acids",
    "https://www.gnfchem.com/gnf-polyvinyl-chloride-pvc-cas-no-9002-86-2",
    "https://www.gnfchem.com/food-additive-fish-collagen-peptide",
    "https://www.gnfchem.com/food-additives-chymosin-cas-no-9001-98-3",
    "https://www.gnfchem.com/stearic-acid",
    "https://www.gnfchem.com/gnf-food-additives-sodium-stearoyl-lactate",
]


def get(url, retries=3):
    for i in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
            return r
        except Exception as e:
            if i == retries - 1:
                print(f"  FAILED: {url} — {e}")
                return None
            time.sleep(2)


def extract_cas(text):
    m = re.search(r'\b(\d{2,7}-\d{2}-\d)\b', text)
    return m.group(1) if m else ""


def clean_name(raw):
    # Remove CAS numbers from end: "... CAS 107-35-7" or "CAS No. ..."
    name = re.sub(r'\s+CAS\s+No?\.?\s*[\d\-]+\s*$', '', raw, flags=re.IGNORECASE).strip()
    # Remove trailing "Manufacturer/Supplier" noise
    name = re.sub(r',\s*(.*?(Manufacturer|Supplier|Factory).*)$', '', name, flags=re.IGNORECASE).strip()
    # Remove SEO one-word prefixes at the start
    name = re.sub(r'^(Wholesale|Bulk|Factory|Hot[\s-]Selling|High[\s-]Quality|Powder)\s+', '', name, flags=re.IGNORECASE).strip()
    # Strip category/grade noise prefixes: e.g. "Food Grade Acidulants Trisodium Citrate" → "Trisodium Citrate"
    # Pattern: if name starts with known category words followed by more words, strip the category prefix
    cat_prefixes = (
        r'^(Food[\s-]Grade|Food[\s-]Additives?|Food[\s-]Ingredients?|Feed[\s-]Grade|'
        r'Pharmaceutical[\s-]Grade|USP[\s-]Grade|Industrial[\s-]Grade|Reagent[\s-]Grade|'
        r'Cosmetic[\s-]Grade|Organic|Health[\s-]Food|Healthy[\s-]Organic|'
        r'Beverage[\s-]Grade|Daily[\s-]Flavor|Light[\s-]Yellow|High[\s-]Dietary[\s-]Fiber|'
        r'Nutritional[\s-]Supplement[s]?|Nutritional[\s-]Supplements?|Nutrient[\s-]Enhancer[\s-]Supplement)\s+'
    )
    name = re.sub(cat_prefixes, '', name, flags=re.IGNORECASE).strip()
    # Strip known category names from beginning if still there
    category_words = (
        r'^(Acidulants?|Amino[\s-]Acids?|Antioxidants?|Cocoa[\s-]Series|'
        r'Dehydrated[\s-]Vegetables?|Emulsifiers?|Enzymes?|Flavorings?|Phosphates?|'
        r'Plant[\s-]Extracts?|Preservatives?|Proteins?|Surfactants?|Sweeteners?|'
        r'Thickeners?|Vitamins?|Acidifiers?)\s+'
    )
    name = re.sub(category_words, '', name, flags=re.IGNORECASE).strip()
    return name


def scrape_product(url):
    r = get(url)
    if not r:
        return None
    soup = BeautifulSoup(r.text, "html.parser")

    # --- category: extract from breadcrumb "You are in: / Home / Category / Product" ---
    category = "Others"
    # Find the breadcrumb container — it contains "You are in" or "You Are In"
    breadcrumb_el = None
    for el in soup.find_all(["div", "p", "nav", "span"]):
        text = el.get_text(" ", strip=True)
        if text.lower().startswith("you are in") or text.lower().startswith("you're in"):
            breadcrumb_el = el
            break
    if not breadcrumb_el:
        # fallback: parent of any element with "you are in" text
        for p in soup.find_all("p"):
            if "you are in" in p.get_text().lower():
                breadcrumb_el = p.parent
                break

    if breadcrumb_el:
        for a in breadcrumb_el.find_all("a", href=True):
            href = a.get("href", "")
            slug = href.rstrip("/").split("/")[-1]
            link_text = a.get_text(strip=True)
            if link_text in CATEGORY_MAP:
                category = CATEGORY_MAP[link_text]
                break
            for key in CATEGORY_MAP:
                if slug == key.lower().replace(" ", "-"):
                    category = CATEGORY_MAP[key]
                    break
            if category != "Others":
                break

    # --- product name (second h1 = product name; first h1 = category) ---
    h1s = soup.find_all("h1")
    raw_name = h1s[1].get_text(strip=True) if len(h1s) > 1 else (h1s[0].get_text(strip=True) if h1s else "")
    name = clean_name(raw_name)

    # --- info list: .pro_info_top ul li ---
    info_items = soup.select(".pro_info_top ul li")
    cas = ""
    available_forms = ""
    for li in info_items:
        text = li.get_text(" ", strip=True)
        # CAS from "Item No : 107-35-7"
        if re.search(r'item\s*no', text, re.IGNORECASE) and not cas:
            cas = extract_cas(text)
        # Available forms from "Color : White Crystalline Powder"
        if re.search(r'\b(color|colour)\b', text, re.IGNORECASE) and not available_forms:
            parts = re.split(r'[:：]', text, maxsplit=1)
            if len(parts) > 1:
                available_forms = parts[1].strip()

    # fallback CAS from name or URL
    if not cas:
        cas = extract_cas(raw_name) or extract_cas(url)

    # --- description and application from .page_prodetail p ---
    all_paras = soup.select(".page_prodetail p")
    description = ""
    app_lines = []
    desc_started = False
    app_started = False

    for p in all_paras:
        txt = p.get_text(" ", strip=True)
        if not txt or len(txt) < 10:
            continue
        # Skip the "Appearance: ... HS CODE: ..." line
        if re.match(r'(Appearance|HS\s*CODE)', txt, re.IGNORECASE):
            continue
        # Skip FAQ, Leave a Message, and similar boilerplate
        if re.search(r'(Can I get.*sample|What.*MOQ|payment terms|place an order|delivery time|quality complaint|Leave A Message|interested in our)', txt, re.IGNORECASE):
            break
        # Application lines start with numbers like "1." or "1:"
        if re.match(r'^\d+[\.\:]', txt):
            app_lines.append(txt)
            app_started = True
            continue
        # Skip "Application", "Specification" headings
        if txt.lower() in ("application", "applications", "specification", "specifications"):
            continue
        # First real paragraph = description
        if not description and len(txt) > 40 and not app_started:
            description = txt

    application = " ".join(app_lines)

    # --- specifications table ---
    specs = ""
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(" ", strip=True) for td in tr.find_all(["th", "td"])]
            cells = [c for c in cells if c]
            if cells:
                rows.append(" | ".join(cells))
        if rows:
            specs = "\n".join(rows)
            break

    full_desc = description.strip()
    if application:
        full_desc = (full_desc + "\n\nApplications:\n" + application).strip()

    return {
        "name": name or raw_name,
        "cas_number": cas,
        "category": category,
        "description": full_desc,
        "specifications": specs,
        "available_forms": available_forms,
        "source_url": url,
    }


def main():
    total = len(PRODUCT_URLS)
    print(f"=== Scraping {total} products from gnfchem.com sitemap ===\n")

    products = []
    skipped = []

    for i, url in enumerate(PRODUCT_URLS, 1):
        slug = url.split("/")[-1][:60]
        print(f"  [{i:3d}/{total}] {slug}")
        p = scrape_product(url)
        if p and p["name"]:
            products.append(p)
        else:
            skipped.append(url)
        time.sleep(0.4)

    output = "scrape_output.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print(f"\n=== Done: {len(products)} products saved to {output} ===")
    if skipped:
        print(f"Skipped {len(skipped)}: {skipped}")

    cats = {}
    for p in products:
        cats[p["category"]] = cats.get(p["category"], 0) + 1
    print("\nProducts per category:")
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
