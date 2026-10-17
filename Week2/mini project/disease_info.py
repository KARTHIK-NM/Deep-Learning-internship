"""
Plant Disease Knowledge Base
Contains disease descriptions, symptoms, severity ratings, causes,
and actionable organic/chemical treatment advice for all supported classes.
"""

DISEASE_DATABASE = {
    "Apple___Black_rot": {
        "crop": "Apple (Malus domestica)",
        "condition": "Black Rot",
        "scientific_name": "Botryosphaeria obtusa (Physalospora obtusa)",
        "is_healthy": False,
        "pathogen_type": "Fungal",
        "severity": "High",
        "color_code": "#e11d48",
        "description": "Black rot causes leaf spots ('frog-eye' leaf spot), fruit rot, and cankers on branches. Infection weakens the tree and significantly degrades fruit yield.",
        "symptoms": [
            "Small purple spots on leaves expanding into circular lesions with light brown centers ('frog-eye' appearance)",
            "Sunken, reddish-brown cankers on bark and woody limbs",
            "Firm, concentric dark decay rings on ripening apples",
            "Mummified fruit hanging on the tree over winter"
        ],
        "organic_treatment": [
            "Prune out dead limbs, diseased twigs, and cankers 6-8 inches below visible infection during dry dormancy.",
            "Remove and destroy all mummified fruits and infected ground leaf litter.",
            "Apply copper sulfate or liquid copper spray at silver-tip leaf bud break.",
            "Spray sulfur or Serenade (Bacillus subtilis bio-fungicide) during the growing season."
        ],
        "chemical_treatment": [
            "Apply Captan 50 WP or Mancozeb starting at pink bud stage through harvest.",
            "Rotate with myclobutanil (Immunox) or kresoxim-methyl to avoid fungicide resistance."
        ],
        "prevention": [
            "Ensure wide tree canopy spacing for rapid drying after rainfall.",
            "Avoid wounding tree bark during mowing and mechanical maintenance.",
            "Sanitize pruning tools in 70% isopropyl alcohol between cuts."
        ]
    },
    "Apple___healthy": {
        "crop": "Apple (Malus domestica)",
        "condition": "Healthy Foliage",
        "scientific_name": "Malus domestica",
        "is_healthy": True,
        "pathogen_type": "None",
        "severity": "None",
        "color_code": "#10b981",
        "description": "The leaf exhibits vibrant chlorophyll pigmentation, robust venation, and zero signs of chlorosis, necrosis, or foliar pathogens.",
        "symptoms": [
            "Uniform deep green color with smooth surface",
            "Intact leaf margins without brown scorching or holes",
            "Absence of spots, mildew, or fungal fruiting bodies"
        ],
        "organic_treatment": [
            "Maintain current organic regimen: seaweed extract spray or compost tea for micronutrient balance.",
            "Mulch base with organic compost or straw to conserve soil moisture."
        ],
        "chemical_treatment": [
            "No chemical treatments required. Avoid unnecessary pesticide applications to protect beneficial insects."
        ],
        "prevention": [
            "Continue regular monitoring for early spring aphids or mites.",
            "Maintain balanced N-P-K fertilization, avoiding excessive nitrogen."
        ]
    },
    "Corn_(maize)___Common_rust_": {
        "crop": "Corn / Maize (Zea mays)",
        "condition": "Common Rust",
        "scientific_name": "Puccinia sorghi",
        "is_healthy": False,
        "pathogen_type": "Fungal",
        "severity": "Moderate to High",
        "color_code": "#f59e0b",
        "description": "Common rust is an airborne fungal disease that attacks maize leaves during cool, humid weather (60-75°F), producing reddish-brown powdery spore pustules that disrupt photosynthesis.",
        "symptoms": [
            "Elongated, cinnamon-brown to golden-red pustules on both upper and lower leaf surfaces",
            "Pustules rupture epidermal tissue, releasing powdery urediniospores",
            "Severe infections turn leaves yellow, dry them out, and lead to premature leaf death",
            "Stunted cob development and poor grain fill"
        ],
        "organic_treatment": [
            "Apply sulfur-based dust or wettable sulfur when rust pustules first emerge.",
            "Foliar spray with Bacillus amyloliquefaciens biological fungicides to inhibit spore germination.",
            "Promptly till crop residue into the soil post-harvest to promote residue decomposition."
        ],
        "chemical_treatment": [
            "Apply strobilurin fungicides (e.g., Azoxystrobin, Pyraclostrobin) or triazoles (e.g., Propiconazole) at first sign of rust if conditions remain cool and wet.",
            "Spray before tasseling (VT stage) for maximum economic benefit."
        ],
        "prevention": [
            "Plant certified rust-resistant maize hybrid cultivars (Rp gene resistance).",
            "Avoid late planting dates when windblown spore loads are at their peak.",
            "Maintain optimal row spacing to enhance airflow and rapid leaf drying."
        ]
    },
    "Corn_(maize)___healthy": {
        "crop": "Corn / Maize (Zea mays)",
        "condition": "Healthy Foliage",
        "scientific_name": "Zea mays",
        "is_healthy": True,
        "pathogen_type": "None",
        "severity": "None",
        "color_code": "#10b981",
        "description": "The maize leaf shows outstanding vigor with clear parallel venation, crisp green blade texture, and no signs of blights, rusts, or pest feeding.",
        "symptoms": [
            "Broad, elongated emerald-green blades with upright posture",
            "Pristine midrib and parallel veins",
            "Absence of lesions, streaks, or chlorotic mottling"
        ],
        "organic_treatment": [
            "Side-dress with composted manure or alfalfa meal during rapid vegetative V6-V10 stage.",
            "Maintain consistent soil moisture through the critical silking and tasseling phases."
        ],
        "chemical_treatment": [
            "No chemical treatments necessary."
        ],
        "prevention": [
            "Practice minimum 2-year crop rotation with legumes or cover crops.",
            "Soil-test annually to maintain balanced nitrogen and potassium levels."
        ]
    },
    "Pepper,_bell___Bacterial_spot": {
        "crop": "Bell Pepper (Capsicum annuum)",
        "condition": "Bacterial Spot",
        "scientific_name": "Xanthomonas campestris pv. vesicatoria",
        "is_healthy": False,
        "pathogen_type": "Bacterial",
        "severity": "High",
        "color_code": "#dc2626",
        "description": "A devastating seed-borne and splash-dispersed bacterial pathogen thriving in warm (75-86°F), rainy environments. Causes widespread foliar defoliation and blistered fruit lesions.",
        "symptoms": [
            "Small, water-soaked, circular to irregular lesions (1-3 mm) on lower leaf surface",
            "Spots turn dark brown or black with a distinct yellow halo",
            "Heavily spotted leaves turn completely chlorotic and drop prematurely, causing sunscald on exposed peppers",
            "Rough, raised, warty scab-like spots on green pepper fruits"
        ],
        "organic_treatment": [
            "Spray fixed copper bactericide combined with Bacillus subtilis (Cease or Serenade).",
            "Immediately rogued and burn heavily infected plants to stop localized airborne spread.",
            "Apply potassium silicate sprays to strengthen plant cell walls against bacterial entry."
        ],
        "chemical_treatment": [
            "Apply copper hydroxide tank-mixed with Mancozeb to overcome copper-resistant Xanthomonas strains.",
            "Use Actigard (acibenzolar-S-methyl) as a plant defense inducer early in the season."
        ],
        "prevention": [
            "Use only certified hot-water treated or disease-free seeds and transplants.",
            "Strictly avoid overhead irrigation; use drip lines at soil level.",
            "Do not handle, weed, or harvest plants while foliage is wet."
        ]
    },
    "Pepper,_bell___healthy": {
        "crop": "Bell Pepper (Capsicum annuum)",
        "condition": "Healthy Foliage",
        "scientific_name": "Capsicum annuum",
        "is_healthy": True,
        "pathogen_type": "None",
        "severity": "None",
        "color_code": "#10b981",
        "description": "Vibrant, glossy pepper foliage exhibiting lush green color, firm turgor pressure, and zero pathogen or insect damage.",
        "symptoms": [
            "Glossy, ovate deep-green leaves with smooth margins",
            "Strong central stems and healthy branch axils",
            "Intact leaves without spotting, curling, or mottling"
        ],
        "organic_treatment": [
            "Apply fish emulsion and liquid kelp every 2-3 weeks to promote strong flowering.",
            "Mulch with straw or black plastic to regulate root temperature and moisture."
        ],
        "chemical_treatment": [
            "No chemical treatments required."
        ],
        "prevention": [
            "Maintain regular calcium supplementation to prevent blossom end rot on developing peppers.",
            "Ensure 3-year solanaceous crop rotation (away from tomatoes, potatoes, eggplants)."
        ]
    },
    "Potato___Early_blight": {
        "crop": "Potato (Solanum tuberosum)",
        "condition": "Early Blight",
        "scientific_name": "Alternaria solani",
        "is_healthy": False,
        "pathogen_type": "Fungal",
        "severity": "Moderate to High",
        "color_code": "#d97706",
        "description": "Early blight is a persistent soil-borne and airborne fungal disease that targets aging potato foliage, creating characteristic 'target board' concentric lesions that compromise tuber development.",
        "symptoms": [
            "Dark brown to black angular lesions on older lower leaves",
            "Concentric rings inside lesions producing a 'bullseye' or target pattern",
            "Yellowing (chlorosis) spreading around individual spots",
            "Premature senescence of lower canopy; dark, leathery sunken lesions on potato tubers"
        ],
        "organic_treatment": [
            "Remove and destroy lower diseased foliage touching the ground.",
            "Apply biofungicide (Streptomyces lydicus or Bacillus amyloliquefaciens).",
            "Spray copper octanoate (copper soap) or neem oil formulations at 7-10 day intervals."
        ],
        "chemical_treatment": [
            "Apply chlorothalonil (Bravo) or Mancozeb protective fungicides prior to canopy closure.",
            "Rotate with azoxystrobin (Quadris) or boscalid (Endura) for systemic protection."
        ],
        "prevention": [
            "Maintain optimal plant nutrition; nitrogen-stressed potatoes are significantly more vulnerable.",
            "Ensure 3-4 year rotation avoiding other Solanaceae family members.",
            "Water early in the morning using drip emitters to prevent prolonged leaf wetness."
        ]
    },
    "Potato___Late_blight": {
        "crop": "Potato (Solanum tuberosum)",
        "condition": "Late Blight",
        "scientific_name": "Phytophthora infestans",
        "is_healthy": False,
        "pathogen_type": "Oomycete (Water Mold)",
        "severity": "Critical",
        "color_code": "#991b1b",
        "description": "Late blight is the historic catastrophic pathogen responsible for the Irish Potato Famine. It can destroy an entire potato crop in 7-10 days under cool, wet conditions (60-70°F, >90% humidity).",
        "symptoms": [
            "Rapidly expanding pale green, water-soaked spots turning into large dark brown/purplish-black blighted areas",
            "Delicate white fuzzy fungal-like sporulation on the underside of leaves during humid mornings",
            "Foul, rotting odor in heavily affected fields",
            "Tubers develop dry, corky, reddish-brown rot penetrating into the flesh"
        ],
        "organic_treatment": [
            "Destroy and bury or trash infected plants immediately; DO NOT compost late blight material.",
            "Apply preventative copper hydroxide or copper oxychloride before wet weather fronts.",
            "Harvest tubers only 2-3 weeks after vine kill so spores on foliage have died."
        ],
        "chemical_treatment": [
            "Apply translaminar/systemic fungicides: Cymoxanil (Curzate), Fluopicolide (Presidio), or Mandipropamid (Revus).",
            "Apply protective Mancozeb or Chlorothalonil every 5-7 days under severe disease alerts."
        ],
        "prevention": [
            "Plant only certified disease-free seed tubers; inspect carefully for rot prior to planting.",
            "Hill soil deeply over growing tubers to create a physical barrier against spore wash-down.",
            "Monitor regional agricultural extension late-blight forecasting and alert bulletins."
        ]
    },
    "Potato___healthy": {
        "crop": "Potato (Solanum tuberosum)",
        "condition": "Healthy Foliage",
        "scientific_name": "Solanum tuberosum",
        "is_healthy": True,
        "pathogen_type": "None",
        "severity": "None",
        "color_code": "#10b981",
        "description": "Robust, upright potato foliage showing vigorous growth, lush compound pinnate leaves, and zero signs of fungal blights or viral mosaics.",
        "symptoms": [
            "Uniform medium-to-deep green compound leaflets",
            "Clean leaf margins without necrotic curling or water soaking",
            "Vigorous branching and strong flowering (if in bloom)"
        ],
        "organic_treatment": [
            "Hill plants with organic mulch or soil when vines reach 6-8 inches tall to protect tubers from greening.",
            "Foliar feed with compost tea or dilute fish hydrolysate for sustained micronutrients."
        ],
        "chemical_treatment": [
            "No chemical treatments required."
        ],
        "prevention": [
            "Inspect underside of leaves weekly for Colorado potato beetle larvae or aphids.",
            "Maintain uniform soil moisture to ensure even tuber expansion without hollow-heart."
        ]
    },
    "Tomato___Early_blight": {
        "crop": "Tomato (Solanum lycopersicum)",
        "condition": "Early Blight",
        "scientific_name": "Alternaria linariae / Alternaria solani",
        "is_healthy": False,
        "pathogen_type": "Fungal",
        "severity": "Moderate to High",
        "color_code": "#ea580c",
        "description": "A very common tomato foliar disease characterized by concentric rings on older lower leaves, progressively defoliating the vine from bottom to top.",
        "symptoms": [
            "Brown-to-black spots with concentric rings ('target' shape) starting on the lowest leaves",
            "Yellow halo encircling each individual spot as toxins spread through leaf tissue",
            "Lower leaves shrivel, turn brown, and drop, exposing fruit to sunscald",
            "Sunken, dark leathery lesions at the fruit stem attachment point"
        ],
        "organic_treatment": [
            "Prune bottom 12-18 inches of foliage once the plant reaches 3 feet to prevent soil splash.",
            "Apply copper-based fungicides (liquid copper soap) or sulfur every 7-10 days.",
            "Biofungicide spray: Bacillus subtilis or Trichoderma harzianum."
        ],
        "chemical_treatment": [
            "Chlorothalonil (Daconil) or Mancozeb protective sprays applied at first sign of disease.",
            "Systemic fungicides: Azoxystrobin (Heritage) or Difenoconazole (Inspire Super)."
        ],
        "prevention": [
            "Thickly mulch the ground with straw, wood shavings, or plastic to eliminate rain splash from soil.",
            "Water exclusively at soil level using soaker hoses or drip tape.",
            "Select resistant cultivars designated with 'EB' (e.g., Mountain Supreme, Defiant PhR)."
        ]
    },
    "Tomato___Late_blight": {
        "crop": "Tomato (Solanum lycopersicum)",
        "condition": "Late Blight",
        "scientific_name": "Phytophthora infestans",
        "is_healthy": False,
        "pathogen_type": "Oomycete (Water Mold)",
        "severity": "Critical",
        "color_code": "#b91c1c",
        "description": "An aggressive, fast-moving pathogen capable of destroying a healthy tomato garden or greenhouse within days in humid, cool to moderate conditions.",
        "symptoms": [
            "Large, irregularly shaped, water-soaked oily spots on leaves turning brown-black",
            "Frosty white fungal-like growth visible on the underside of leaves in moist morning humidity",
            "Dark brown to purplish cankers girdling stems and branches",
            "Green and ripe fruits turn dark, firm, and greasy-brown with corrugated rot"
        ],
        "organic_treatment": [
            "Bag and discard infected plant tissues immediately in landfill waste; DO NOT compost.",
            "Preventative sprays of copper octanoate or copper hydroxide prior to anticipated rainy periods.",
            "Ensure plants are staked and trellised for maximum ventilation and wind movement."
        ],
        "chemical_treatment": [
            "Apply preventative Chlorothalonil or Mancozeb before disease appearance.",
            "Under high disease pressure: Propamocarb (Previcur Flex), Dimethomorph (Forum), or Mandipropamid (Revus)."
        ],
        "prevention": [
            "Select late-blight resistant tomato varieties (e.g., Mountain Magic, Defiant, Jasper, Iron Lady).",
            "Avoid overhead sprinkler watering; keep foliage completely dry overnight.",
            "Eliminate volunteer potato and tomato plants around the garden perimeter."
        ]
    },
    "Tomato___healthy": {
        "crop": "Tomato (Solanum lycopersicum)",
        "condition": "Healthy Foliage",
        "scientific_name": "Solanum lycopersicum",
        "is_healthy": True,
        "pathogen_type": "None",
        "severity": "None",
        "color_code": "#10b981",
        "description": "Exemplary tomato foliage showing deep green color, vigorous serrated leaflets, and optimal glandular trichomes without any sign of blight or viral infection.",
        "symptoms": [
            "Lush, deeply serrated dark-green leaflets with clear veins",
            "Strong turgid stems and fragrant foliage",
            "Absence of wilting, chlorotic rings, spots, or powdery mildew"
        ],
        "organic_treatment": [
            "Prune non-fruiting suckers to enhance airflow through the main canopy.",
            "Apply compost tea, worm casting tea, or kelp meal every 2 weeks."
        ],
        "chemical_treatment": [
            "No chemical treatments required."
        ],
        "prevention": [
            "Ensure consistent deep watering to avoid calcium transport issues and blossom end rot.",
            "Maintain 3-foot spacing between plants and 4-foot spacing between rows."
        ]
    }
}

def get_disease_details(class_id):
    """Retrieve detailed disease profile for a given class name."""
    if class_id in DISEASE_DATABASE:
        return DISEASE_DATABASE[class_id]
    
    # Fallback for unknown classes
    parts = class_id.split("___")
    crop = parts[0].replace("_", " ").title() if len(parts) > 0 else "Plant"
    condition = parts[1].replace("_", " ").title() if len(parts) > 1 else "Unknown"
    is_healthy = "healthy" in class_id.lower()
    
    return {
        "crop": crop,
        "condition": condition,
        "scientific_name": f"{crop} spec.",
        "is_healthy": is_healthy,
        "pathogen_type": "Unknown" if not is_healthy else "None",
        "severity": "Moderate" if not is_healthy else "None",
        "color_code": "#10b981" if is_healthy else "#ea580c",
        "description": f"Diagnosis for {crop} showing signs of {condition}.",
        "symptoms": ["Visible foliar changes on leaf surface."],
        "organic_treatment": ["Isolate affected leaves and monitor watering."],
        "chemical_treatment": ["Consult your local agricultural extension service."],
        "prevention": ["Ensure balanced fertilization and proper airflow."]
    }
