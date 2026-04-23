"""
Clean scrape_output.json into clean_output.json.
Fixes: product names, categories, descriptions, available_forms, CAS numbers.
Usage: python clean_scraped_products.py [--input scrape_output.json] [--output clean_output.json]
"""
import json
import re
import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# Explicit name corrections (old name → clean name)
# ---------------------------------------------------------------------------
NAME_MAP = {
    "Trisodium Citrate CAS 6132-04-3": "Trisodium Citrate",
    "DL-Tartaric Acid White Granule  Powder CAS 133-37-9": "DL-Tartaric Acid",
    "Food Industry Food Acidulant  Lactic Acid Yellow Liquid CAS 50-21-5": "Lactic Acid",
    "DL-Malic Acid White Crystalline Granule Powder CAS 617-48-1/6915-15-7": "DL-Malic Acid",
    "Food Grade Potassium Citrate CAS 866-84-2": "Potassium Citrate",
    "Fumaric Acid White Powder CAS 110-17-8": "Fumaric Acid",
    "Grade Acidifiers Flavoring Agents Citric Acid CAS 5949-29-1": "Citric Acid",
    "Acetic Acid CAS 64-19-7": "Acetic Acid",
    "Food Grade Amino Acids Creatine Mono Powder CAS 6020-87-7": "Creatine Monohydrate",
    "Weight Loss White Powder Acetyl L- Carnitine HCL CAS 5080-50-2": "Acetyl-L-Carnitine HCl",
    "White Powder Amino Acids Skin Whitening Cosmetic Grade Theanine CAS 3081-61-6": "L-Theanine",
    "Food Grade Glucosamine Chondroitin Sulfate CAS 29031-19-4": "Chondroitin Sulfate",
    "Nutritional Supplement  Water-Soluble L-Carnitine Tartrate CAS 541-15-1": "L-Carnitine Tartrate",
    "Food Addition Amino Acids L-Valine White Powder CAS 72-18-4": "L-Valine",
    "Feed Grade Amino Acids Feed Grade L-threonine 98.5% (Feed Grade) CAS 72-19-5": "L-Threonine",
    "Feed Grade Amino Acids Light Gray Crystal DL Methionine（Feed Grade) CAS 59-51-8": "DL-Methionine",
    "L-Carnitine Fumarate Food Grade L-Carnitine Fumarate CAS 90471-79-7": "L-Carnitine Fumarate",
    "Food Additives  Methyl Sulfonyl Methane (MSM) CAS 67-71-0": "Methylsulfonylmethane (MSM)",
    "Healthy Nourishment Nutrition L-Glutamine Powder CAS 56-85-9": "L-Glutamine",
    "Lipid Metabolism Food Supplement Nutritional Supplements L-Carnitine CAS 541-15-1": "L-Carnitine",
    "Nutritional Taurine CAS 107-35-7": "Taurine",
    "Preservative Sodium Methyl Paraben CAS 5026-62-0": "Sodium Methylparaben",
    "Food Additives Cocoa Series Alkalized Coco Powder": "Alkalized Cocoa Powder",
    "Ingredients Food Additives Natural Coco Powder": "Natural Cocoa Powder",
    "Ethanolamine Powder CAS 141-43-5": "Ethanolamine",
    "Tarquinor Food Additives Halquinol CAS 8067-69-4": "Halquinol",
    "EnzymeTransglutaminase-TX10 CAS 80146-85-6": "Transglutaminase TX10",
    "Enzymatic preparation Transglutaminase TX06 CAS 80146-85-6": "Transglutaminase TX06",
    "Additives Enzyme β-Nicotinamide Mononucleotide(Grade I) CAS 1094-61-7": "β-Nicotinamide Mononucleotide (NMN)",
    "Preservative Propyl Paraben CAS 94-13-3": "Propyl Paraben",
    "Food Additives Sodium Propyl Paraben CAS 35285-69-9": "Sodium Propyl Paraben",
    "Methyl Paraben CAS 99-76-3": "Methyl Paraben",
    "Silicon Dioxide CAS 7631-86-9": "Silicon Dioxide",
    "Food Additives Titanium Dioxide(Rutile|Anatase) CAS 13463-67-7": "Titanium Dioxide",
    "Sodium Isoascorbate Erythorbic Acid CAS 89-65-6": "Erythorbic Acid",
    "Sodium Ascorbate CAS 134-03-2": "Sodium Ascorbate",
    "Ascorbic Acid(Vitamin C) CAS 50-81-7": "Ascorbic Acid (Vitamin C)",
    "Vitamin C Palmitate  Ascorbyl Palmitate CAS 137-66-6": "Ascorbyl Palmitate",
    "Isoascorbate Sodium Erythorbate CAS 6381-77-7": "Sodium Erythorbate",
    "Additives Vegetable Extract Dehydrate Tomato Powder": "Dehydrated Tomato Powder",
    "Grade Vegetables Dehydrate Onion Powder": "Dehydrated Onion Powder",
    "Grade Dehydrate Onion Flakes haracteristic FlavorIntroduction  Food Grade": "Dehydrated Onion Flakes",
    "Kiln Dehydrate Garlic Flakes Food Grade": "Dehydrated Garlic Flakes",
    "Enzyme Food Additives Soya Lecithin Liquid CAS 8002-43-5": "Soy Lecithin Liquid",
    "Food Additives Food Grade Soy Lecithin Powder CAS 8002-43-5": "Soy Lecithin Powder",
    "Food Grade Propylene Glycol CAS 57-55-6": "Propylene Glycol",
    "USP Food Grade Emulsifiers Food Additives Glycerin 99.5% CAS 56-81-5": "Glycerin",
    "Distilled Glycerin Monostearate(DGM) CAS 31566-31-1": "Glycerin Monostearate (GMS)",
    "Ethyl maltol Flavor Enhancers Flavorings Maltol CAS 118-71-8": "Maltol",
    "Molasses Yeast Flavorings Food Additives Emulsifier Instant Dry Yeast": "Instant Dry Yeast",
    "Food Additives Menthol Crystal White Crystal CAS 89-78-1": "Menthol Crystals",
    "Food Flavor Food Additives Ethyl Maltol CAS 118-71-8": "Ethyl Maltol",
    "Food Grade Flavor Enhancers Ethyl Vanillin CAS 121-33-5": "Ethyl Vanillin",
    "Food Additives Monosodium Glutamate 99% CAS 142-47-2": "Monosodium Glutamate (MSG)",
    "Flavor Enhancers Food Additives Grade Vanillin CAS 121-33-5": "Vanillin",
    "Food Additives Feed Grade Sodium Bicarbonate CAS 144-55-8": "Sodium Bicarbonate",
    "Pectin Curing Agent Tricalcium Phosphate CAS 7758-87-4": "Tricalcium Phosphate",
    "Detergent Food Ingredients Additives Trisodium Phosphate CAS 7601-54-9": "Trisodium Phosphate",
    "Grade Phosphoric Acid CAS 7664-38-2": "Phosphoric Acid",
    "Blend Compound Food Phosphate CAS 10124-56-8": "Compound Food Phosphate Blend",
    "Sodium Hexametaphosphate(SHMP) CAS 10124-56-8": "Sodium Hexametaphosphate (SHMP)",
    "Food Grade Additives Sodium Acid Pyrophosphate(SAPP) CAS 7758-16-9": "Sodium Acid Pyrophosphate (SAPP)",
    "Industrial Food Additives Grade Sodium Tripolyphosphate CAS 7758-29-4": "Sodium Tripolyphosphate (STPP)",
    "Food Additives Plant Extracts Moringa Oleifera Leaf Powder": "Moringa Oleifera Leaf Powder",
    "Health Organic Food Additives Tribulus Terrestris Extract CAS 90131-68-3": "Tribulus Terrestris Extract",
    "Food Additives Ingredients Chlorella Powder": "Chlorella Powder",
    "Food Grade Ingredients Organic Inulin": "Inulin",
    "Food Grade Additives Glycyrrhizin Acid Licorice extract CAS 1405-86-3": "Licorice Extract (Glycyrrhizin)",
    "Industrial Grade Food Additives Grade EDTA 4Na CAS 13235-36-4": "EDTA Tetrasodium (EDTA-4Na)",
    "Food Additives Grade Benzoic Acid CAS 65-85-0": "Benzoic Acid",
    "Thickening Agent Food Additives Sodium Acetate (Anhydrous) CAS 4075-81-4": "Sodium Acetate (Anhydrous)",
    "Grade Antioxidant Glucono-Delta-Lactone(GDL) CAS 90-80-2": "Glucono-Delta-Lactone (GDL)",
    "Acidity Regulators Food Additives Grade Sodium Propionate CAS 6132-04-3": "Sodium Propionate",
    "Grade Preservative Sodium Benzoate CAS 532-32-1": "Sodium Benzoate",
    "Food Grade Calcium Propionate CAS 4075-81-4": "Calcium Propionate",
    "Food Additives Potassium Sorbate Granular CAS 590-00-1": "Potassium Sorbate",
    "Food Additives Grade Healthy Sorbic Acid CAS 110-44-1": "Sorbic Acid",
    "Food Preservative Food Grade Additives Natamycin CAS 7681-93-8": "Natamycin",
    "Food Additives Food Grade Nisin CAS 1414-45-5": "Nisin",
    "Soybean Powder Food Grade Food Additives Pea Fiber": "Pea Fiber",
    "Stabilizer Healthy Textured Soy Protein CAS 9000-10-0": "Textured Soy Protein (TSP)",
    "Food Grade Rice Protein CAS N/A": "Rice Protein",
    "Acids Feed Grade Food Additives Hydrolyzed Animal Protein CAS 92113-31-0": "Hydrolyzed Animal Protein",
    "Additives Acidity Regulators Dietary Soy Fiber CAS 9000-70-8": "Soy Dietary Fiber",
    "Grade Organic Pea Protein CAS 90-10-0": "Pea Protein Isolate",
    "Health Foods Beverage Grade Organic Hemp Protein": "Hemp Protein",
    "Grade Proteins Vital Wheat Gluten CAS 8002-80-0": "Vital Wheat Gluten",
    "Food Grade Soy Protein Concentrate CAS N/A": "Soy Protein Concentrate",
    "Grade Protein Isolated Soy Protein(ISP) CAS 9010-10-0": "Isolated Soy Protein (ISP)",
    "Grade Sweeteners Dextrose Monohydrate CAS 5996-10-1": "Dextrose Monohydrate",
    "Food Industry Food Additives Grade Neotame CAS 165450-17-9": "Neotame",
    "Grade Sweeteners Erythritol CAS 149-32-6": "Erythritol",
    "Grade Confectionery Crystalline Fructose CAS 57-48-7": "Crystalline Fructose",
    "Food Grade Allulose(D-allulose,D-Psicose) CAS 551-68-8": "Allulose (D-Psicose)",
    "Dietary Fiber Food Additives Grade Poly-D-glucose Polyglucose CAS 68424-04-4": "Polydextrose",
    "Grade Sweeteners Maltitol 75% CAS 585-88-6": "Maltitol Syrup 75%",
    "Food Additives Blending for Monk Fruit & Erythritol CAS 149-32-6": "Monk Fruit & Erythritol Blend",
    "Food Ingredients Sweeteners Sodium Saccharin CAS 204-886-1": "Sodium Saccharin",
    "Food Additives Grade Food Industry Xylitol CAS 87-99-0": "Xylitol",
    "Food Additives Grade Sodium Cyclamate CAS 68476-78-8": "Sodium Cyclamate",
    "Grade Beverage Grade Acesulfame K CAS 33665-90-6": "Acesulfame K",
    "Food Additives Confectionery Grade Sucralose CAS 56038-13-2": "Sucralose",
    "Food Additives Food Grade Sweeteners Aspartame CAS 22839-47-0": "Aspartame",
    "Additives Emulsifiers Thickeners Xanthan Gum CAS 11138-66-2": "Xanthan Gum",
    "Citrus Pectin CAS 9000-69-5": "Citrus Pectin",
    "Absorbent Surfactant Food Additives Grade Sodium Alginate CAS 9005-38-3": "Sodium Alginate",
    "Beverage Grade Gelatin(Beef,Pork & Fish based) CAS 9000-70-8": "Gelatin (Beef, Pork & Fish)",
    "Grade Thickeners Carrageenan Kappa Refiend CAS 9000-07-1": "Carrageenan Kappa Refined",
    "Food Garde Additives Kappa Carrageenan Semi-Refined CAS 9000-07-1": "Carrageenan Kappa Semi-Refined",
    "Grade Thickeners Stabilizers Sodium Carboxymethyl Cellulose(CMC) CAS 9004-32-4": "Sodium Carboxymethyl Cellulose (CMC)",
    "Grade Thickeners Xanthan Gum 200mesh CAS 11138-66-2": "Xanthan Gum 200 Mesh",
    "Food Additives Emulsifiers Nutrient Enhancers Apple Pectin CAS 9000-70-8": "Apple Pectin",
    "Food Additives Grade Stabilizers Agar Agar CAS 9002-18-0": "Agar-Agar",
    "Grade Stabilizers Thickeners Xanthan Gum 80mesh CAS 11138-66-2": "Xanthan Gum 80 Mesh",
    "Konjac Gum CAS 37220-17-0": "Konjac Glucomannan",
    "Food Additives Health Food Vitamin B5 CAS 16485-10-2": "Vitamin B5 (Calcium Pantothenate)",
    "Food Ingredients Food Additives Grade Vitamin B3 CAS 98-92-0": "Vitamin B3 (Niacinamide)",
    # Vitamins with noisy names
    "Grade Nutritional Enhancers Feed Grade D-Biotin(Vitamin H) CAS 58-85-5": "Vitamin H (D-Biotin)",
    "Grade Nutritional Enhancers Vitamin E Powder CAS 58-56-0": "Vitamin E Powder",
    "Acidity Regulators Food Additives Grade Ascorbic Acid(Vitamin C) CAS 50-81-7": "Vitamin C (Ascorbic Acid)",
    "Health Food Food Grade Stabilizers Vitamin B6 CAS 58-56-0": "Vitamin B6 (Pyridoxine HCl)",
    "Grade Animal Feed Feed Grade Vitamin B1 Mononitrate CAS 59-43-8": "Vitamin B1 (Thiamine Mononitrate)",
    "Food Additives Food Supplements Health Food Nutritional Enhancers Vitamin b1 HCL CAS 59-43-8": "Vitamin B1 (Thiamine HCl)",
    "Food Additives Food Grade  Health Food Vitamin B9/Folic Acid": "Vitamin B9 (Folic Acid)",
    # Flavorings
    "Essence and fragrance Laurel Leaf": "Laurel Leaf (Bay Leaf)",
    "Essence and fragrance GNF Condiment Star anise": "Star Anise",
    # Emulsifiers / Other
    "GNF Food additives Sodium stearoyl lactylate": "Sodium Stearoyl Lactylate (SSL)",
    "GNF Food additives Stearic Acid CAS 57-11-4": "Stearic Acid",
    # More vitamins
    "Food Additives Grade Vitamin B12 Cyanocobalamin CAS 68-19-9": "Vitamin B12 (Cyanocobalamin)",
    "Food Additives Grade Inositol CAS 87-89-8": "Inositol",
    "Food Additives Grade Vitamin E Oil 98% CAS 7695-91-2": "Vitamin E Oil 98%",
    "Food Additives Grade Healthy Organic Beta Carotene": "Beta Carotene",
    "Grade Healthy Organic Energy Metabolism Vitamin B2 (Riboflavin)": "Vitamin B2 (Riboflavin)",
    "Food Additives Plant Extracts Exercise Supplement Vitamin b12 Methylcobalamin": "Vitamin B12 Methylcobalamin",
    "E feed grade Antibiotics and antimicrobials Immunity enhancement": "Vitamin E (Feed Grade)",
    # Surfactants
    "Sodium Lauryl Ether Sulfate SLES 70% Surfactant Supplier CAS:68585-34-2": "Sodium Lauryl Ether Sulfate (SLES)",
    # Sweeteners with noisy names
    "Grade Food Ingredient Maltodextrin CAS 9050-36-6": "Maltodextrin",
    "High-purity food grade Mannitol Sweetener CAS NO：69-65-8": "Mannitol",
    "Stevia Extract CAS NO：57817-89-7 Food Additive Sweetener": "Stevia Extract",
    # Miscellaneous
    "fish collagen peptide": "Fish Collagen Peptide",
}

# ---------------------------------------------------------------------------
# Products to remove entirely (not food additives / clearly irrelevant)
# ---------------------------------------------------------------------------
SKIP_CAS = {
    "9002-86-2",   # Polyvinyl chloride (PVC) — not a food additive
}

# Products to skip based on name fragment (when CAS is shared with a real product)
SKIP_NAME_FRAGMENTS = [
    "Oil Drilling Grade",  # Xanthan Gum oil drilling variant
]

# ---------------------------------------------------------------------------
# Category corrections (CAS or product name → correct category)
# ---------------------------------------------------------------------------
CATEGORY_FIXES = {
    # Parabens are preservatives, not antioxidants
    "5026-62-0": "Preservatives",   # Sodium Methylparaben
    "94-13-3":   "Preservatives",   # Propyl Paraben
    "35285-69-9":"Preservatives",   # Sodium Propyl Paraben
    "99-76-3":   "Preservatives",   # Methyl Paraben
    # Silicon dioxide & titanium dioxide are not antioxidants
    "7631-86-9": "Others",          # Silicon Dioxide (anti-caking)
    "13463-67-7":"Others",          # Titanium Dioxide (food color)
    # Stearic Acid is an emulsifier, not a preservative
    "57-11-4":   "Emulsifiers",
    # NMN is a nutritional supplement, not an enzyme
    "1094-61-7": "Nutritional Supplements",
    # Sodium bicarbonate is a leavening/pH agent, not a phosphate
    "144-55-8":  "Others",
}

# ---------------------------------------------------------------------------
# CAS corrections  { wrong_cas: (correct_cas, product_name_fragment) }
# A fragment must be present in the product name for the fix to apply
# ---------------------------------------------------------------------------
CAS_FIXES = {
    # DL-Tartaric Acid incorrectly inherited Trisodium Citrate's CAS (scraper bug)
    ("6132-04-3", "tartaric"): "133-37-9",
}

# ---------------------------------------------------------------------------
# Forms that are clearly NOT physical forms — replace with empty string so
# staff can fill in properly, or use a known fallback from the name/description
# ---------------------------------------------------------------------------
BAD_FORMS_PATTERNS = [
    r"^T/T",          # payment terms
    r"CREDIT PAYMENT",
    r"CAS\s*\d",      # CAS number leaked in
    r"Sodium Propyl",  # product names
    r"Sodium Ascorbate",
    r"White Powder Silicon",
    r"Ethyl maltol$",
    r"DL-Tartaric Acid White",
    r"L-Valine White Powder$",
    r"Propyl Paraben$",
]

# Descriptors to strip from forms (keep only the actual form type)
FORM_CLEANUP_SUBS = [
    (r"^Pure\s+", ""),
    (r"\s+No Obvious Dark Spots$", ""),
    (r"^Natural\s+", ""),
    (r"\s+Manufacturer$", ""),
    (r"^Colorless and Transparent$", "Colorless Transparent Liquid"),
    (r"^Colorless Tansparent$", "Colorless Transparent Liquid"),
    (r"^Colorless Transparent$", "Colorless Transparent Liquid"),
    (r"^White Almost White Crystalline Powder$", "White Crystalline Powder"),
    (r"^White Crystall Powder$", "White Crystalline Powder"),
    (r"^White Crystals Powder$", "White Crystalline Powder"),
    (r"^White Crystal$", "White Crystalline Powder"),
    (r"^White Crystal Powder$", "White Crystalline Powder"),
    (r"^White$", "White Powder"),
    (r"^Light Yellow$", "Light Yellow Powder"),
    (r"^Yellow or Yellowish$", "Yellow Granules"),
    (r"^Light Free Flowing Powder$", "Light Yellow Free-Flowing Powder"),
    (r"^White Yellowish Powder$", "White to Light Yellow Powder"),
    (r"^White To Light Yellow$", "White to Light Yellow Powder"),
    (r"^Pink, Green, Red, White Customized$", "Powder (various colours available)"),
    (r"^Pure White  Milk White$", "White Powder"),
    (r"^Light Yellow Cream Color$", "Light Yellow Powder"),
    (r"^Light Yellow or Creamy$", "Light Yellow to Cream Powder"),
]

# ---------------------------------------------------------------------------
# Description cleaning helpers
# ---------------------------------------------------------------------------
# FAQ question patterns inserted by the competitor's site
FAQ_PATTERNS = [
    # "Applications:\n1. What is ..." FAQ blocks
    re.compile(
        r"\n\nApplications:\s*\n\d+[\.\:][^\n]*\?.*",
        re.DOTALL,
    ),
    # FAQ numbers at the end without "Applications:" header
    re.compile(
        r"\n\d+[\.\:]\s+What (?:is|are|specifications|certifications|the|does)[^\n]*\?.*",
        re.DOTALL,
    ),
    # Lone percentage/number fragments that leaked in from specs
    re.compile(r"\n\n\d+\.\d+%.*$", re.DOTALL),
    # "0.5ppm NMT" type fragment
    re.compile(r"\s+\d+\.\d+ppm\s+NMT\b.*$", re.DOTALL),
    # Stray spec value fragments at end  e.g. "98.0-102.0%"
    re.compile(r"\s+\d{2,3}\.\d+-\d{2,3}\.\d+%\s*$"),
    # "0.1ppm Max" fragments
    re.compile(r"\s+\d+\.\d+ppm\s+Max\b.*$", re.DOTALL),
    # "91.53%(HPLC)" at end of description
    re.compile(r"\s+\d+\.\d+%\s*\([A-Z]+\)\s*$"),
]

# Bracket format codes from enzyme descriptions  [Model] TG-TX10  etc.
BRACKET_CODE_RE = re.compile(r"\[(\w[\w\s/]+?)\]\s*")


def clean_enzyme_description(desc: str) -> str:
    """Convert [Field] Value format to readable prose."""
    if "[Model]" not in desc and "[Color]" not in desc:
        return desc
    # Extract key fields into a summary paragraph
    fields = {}
    for match in re.finditer(r"\[([A-Za-z /]+)\]\s*([^\[]+?)(?=\[|$)", desc, re.DOTALL):
        key = match.group(1).strip()
        val = match.group(2).strip().rstrip(".")
        fields[key] = val
    parts = []
    if "Model" in fields:
        parts.append(f"Model: {fields['Model']}.")
    if "Color" in fields:
        parts.append(f"Appearance: {fields['Color']}.")
    if "Technological Characteristics" in fields:
        parts.append(fields["Technological Characteristics"])
    if "Ingredients" in fields:
        parts.append(f"Ingredients: {fields['Ingredients']}.")
    if "Product Application" in fields:
        parts.append(f"Application: {fields['Product Application']}.")
    if "Dosage" in fields:
        parts.append(f"Recommended dosage: {fields['Dosage']}.")
    return " ".join(parts) if parts else desc


def clean_description(desc: str) -> str:
    if not desc:
        return desc
    # Handle enzyme bracket format first
    desc = clean_enzyme_description(desc)
    # Strip FAQ question blocks
    for pattern in FAQ_PATTERNS:
        desc = pattern.sub("", desc)
    # Remove lines that are just a lone spec value like "Grade Standard: Food Grade"
    lines = desc.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Skip lines that are just bare spec data
        if re.match(r"^Grade Standard:\s*\w", stripped):
            continue
        if re.match(r"^Store in (?:well ventilated|cool|tight)", stripped):
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def clean_available_forms(forms: str) -> str:
    if not forms:
        return forms
    # Check if it matches a bad pattern → blank it out
    for pattern in BAD_FORMS_PATTERNS:
        if re.search(pattern, forms, re.IGNORECASE):
            return ""
    # Apply cleanup substitutions
    result = forms.strip()
    for pat, replacement in FORM_CLEANUP_SUBS:
        result = re.sub(pat, replacement, result, flags=re.IGNORECASE).strip()
    return result


def clean_name_fallback(name: str) -> str:
    """Generic name cleaning: strip known SEO prefixes and CAS suffixes."""
    # Remove trailing " CAS XXXX-XX-X" or " CAS XXXX-XX-X/YYYY-YY-Y"
    name = re.sub(r"\s+CAS\s+[\d\-/]+\s*$", "", name, flags=re.IGNORECASE).strip()
    # Remove trailing " N/A"
    name = re.sub(r"\s+N/A\s*$", "", name, flags=re.IGNORECASE).strip()
    # Strip leading generic prefixes (order matters — most specific first)
    PREFIXES = [
        r"^Food Additives\s+",
        r"^Food Additive\s+",
        r"^Food Ingredients\s+",
        r"^Food Ingredient\s+",
        r"^Food Industry\s+",
        r"^Food Grade\s+",
        r"^Food Grade Additives\s+",
        r"^Feed Grade Amino Acids\s+",
        r"^Feed Grade\s+",
        r"^Health Foods\s+",
        r"^Health Organic\s+",
        r"^Health Organic Food Additives\s+",
        r"^Healthy\s+",
        r"^Nutritional Supplement\s+",
        r"^Nutritional Supplements\s+",
        r"^Dietary Fiber\s+",
        r"^Industrial Grade\s+",
        r"^Industrial Food Additives Grade\s+",
        r"^USP (?:Food )?Grade\s+",
        r"^Grade\s+",
        r"^Organic\s+",
        r"^Beverage Grade\s+",
        r"^Cosmetic Grade\s+",
        r"^Pharmaceutical Grade\s+",
        r"^Reagent Grade\s+",
        r"^Confectionery Grade\s+",
        # Category names used as prefix
        r"^(?:Sweeteners|Acidulants|Thickeners|Emulsifiers|Preservatives|Antioxidants"
        r"|Flavorings|Proteins|Amino Acids|Vitamins|Phosphates|Plant Extracts"
        r"|Enzymes|Nutritional Supplements|Cocoa Series|Dehydrated Vegetables"
        r"|Surfactants|Others)\s+",
        # Compound prefix patterns
        r"^(?:Food (?:Grade )?)?Additives\s+",
        r"^Additives\s+",
        r"^Acids Feed Grade\s+",
    ]
    for prefix in PREFIXES:
        name = re.sub(prefix, "", name, flags=re.IGNORECASE).strip()
    # Collapse multiple spaces
    name = re.sub(r"\s{2,}", " ", name)
    return name.strip()


def fix_cas(product: dict) -> str:
    cas = product.get("cas_number", "")
    name_lower = product.get("name", "").lower()
    for (wrong_cas, name_fragment), correct in CAS_FIXES.items():
        if cas == wrong_cas and name_fragment in name_lower:
            return correct
    return cas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="scrape_output.json")
    parser.add_argument("--output", default="clean_output.json")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} products from {input_path}")

    cleaned = []
    name_changes = 0
    cat_changes = 0
    desc_changes = 0
    form_changes = 0
    cas_changes = 0
    skipped = 0

    for item in data:
        if item.get("cas_number", "") in SKIP_CAS:
            print(f"  REMOVED: {item['name']}")
            skipped += 1
            continue
        if any(frag in item.get("name", "") for frag in SKIP_NAME_FRAGMENTS):
            print(f"  REMOVED: {item['name']}")
            skipped += 1
            continue
        original_name = item["name"]

        # --- Name ---
        if original_name in NAME_MAP:
            new_name = NAME_MAP[original_name]
        else:
            new_name = clean_name_fallback(original_name)
        if new_name != original_name:
            name_changes += 1

        # --- CAS ---
        new_cas = fix_cas(item)
        if new_cas != item.get("cas_number", ""):
            cas_changes += 1

        # --- Category ---
        cas_for_cat = new_cas or item.get("cas_number", "")
        if cas_for_cat in CATEGORY_FIXES:
            new_cat = CATEGORY_FIXES[cas_for_cat]
        else:
            new_cat = item["category"]
        if new_cat != item["category"]:
            cat_changes += 1

        # --- Description ---
        new_desc = clean_description(item.get("description", ""))
        if new_desc != item.get("description", ""):
            desc_changes += 1

        # --- Available forms ---
        new_forms = clean_available_forms(item.get("available_forms", ""))
        if new_forms != item.get("available_forms", ""):
            form_changes += 1

        cleaned.append({
            "name": new_name,
            "cas_number": new_cas,
            "category": new_cat,
            "description": new_desc,
            "specifications": item.get("specifications", ""),
            "available_forms": new_forms,
            "source_url": item.get("source_url", ""),
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print(f"\nClean output written to {output_path}")
    print(f"  Names changed:       {name_changes}")
    print(f"  CAS fixed:           {cas_changes}")
    print(f"  Categories fixed:    {cat_changes}")
    print(f"  Descriptions cleaned:{desc_changes}")
    print(f"  Forms cleaned:       {form_changes}")
    print(f"  Products removed:    {skipped}")


if __name__ == "__main__":
    main()
