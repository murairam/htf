"""
Product Data and Image Analysis for ACE Plant-Based Packaging Intelligence.

Handles:
1. Fetching from OpenFoodFacts API
2. Normalizing to required plant-based schema
3. GPT Vision API image analysis for packaging description and improvements
"""
import json
import base64
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict

from . import config as config_module
from .config import PLANT_BASED_CATEGORIES


# =============================================================================
# NORMALIZED PRODUCT DATA SCHEMA
# =============================================================================

@dataclass
class Nutriments:
    """Normalized nutriments for plant-based analysis."""
    proteins_100g: float = 0.0
    fiber_100g: float = 0.0
    salt_100g: float = 0.0
    sugars_100g: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        return asdict(self)
    
    @classmethod
    def from_openfoodfacts(cls, nutriments: dict) -> "Nutriments":
        return cls(
            proteins_100g=float(nutriments.get("proteins_100g", 0) or 0),
            fiber_100g=float(nutriments.get("fiber_100g", 0) or 0),
            salt_100g=float(nutriments.get("salt_100g", 0) or 0),
            sugars_100g=float(nutriments.get("sugars_100g", 0) or 0)
        )


@dataclass
class Packaging:
    """Normalized packaging information."""
    materials: List[str] = field(default_factory=list)
    recyclable: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_openfoodfacts(cls, product: dict) -> "Packaging":
        materials = []
        packaging_tags = product.get("packaging_tags", [])
        packaging_text = product.get("packaging", "")
        
        # Extract materials from tags
        material_keywords = ["plastic", "paper", "cardboard", "glass", "metal", "aluminum", "steel", "wood", "compostable", "biodegradable"]
        for tag in packaging_tags:
            tag_lower = tag.lower().replace("en:", "").replace("fr:", "")
            for kw in material_keywords:
                if kw in tag_lower and kw not in materials:
                    materials.append(kw)
        
        # Check packaging text
        for kw in material_keywords:
            if kw in packaging_text.lower() and kw not in materials:
                materials.append(kw)
        
        # Determine recyclability
        recyclable = any(r in str(packaging_tags).lower() for r in ["recyclable", "recycled", "recycle"])
        
        return cls(materials=materials, recyclable=recyclable)


@dataclass
class NormalizedProductData:
    """
    Normalized product data for plant-based analysis.
    
    This is the ONLY structure used for scoring and reasoning.
    All fields are critical for plant-based perception, trust, pricing,
    and go-to-market decisions.
    """
    product_id: str = ""  # EAN barcode
    name: str = ""
    brand: str = ""
    plant_based_category: str = ""  # Derived from categories_tags
    ingredients_text: str = ""
    ingredients_count: int = 0
    additives_count: int = 0
    nova_group: int = 0  # 1-4, ultra-processing indicator
    nutriscore: str = ""  # A-E or empty
    nutriments: Nutriments = field(default_factory=Nutriments)
    labels: List[str] = field(default_factory=list)  # organic, vegan, etc.
    packaging: Packaging = field(default_factory=Packaging)
    origin: str = ""
    countries: List[str] = field(default_factory=list)
    image_front_url: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "brand": self.brand,
            "plant_based_category": self.plant_based_category,
            "ingredients_text": self.ingredients_text,
            "ingredients_count": self.ingredients_count,
            "additives_count": self.additives_count,
            "nova_group": self.nova_group,
            "nutriscore": self.nutriscore,
            "nutriments": self.nutriments.to_dict(),
            "labels": self.labels,
            "packaging": self.packaging.to_dict(),
            "origin": self.origin,
            "countries": self.countries,
            "image_front_url": self.image_front_url
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NormalizedProductData":
        return cls(
            product_id=data.get("product_id", ""),
            name=data.get("name", ""),
            brand=data.get("brand", ""),
            plant_based_category=data.get("plant_based_category", ""),
            ingredients_text=data.get("ingredients_text", ""),
            ingredients_count=data.get("ingredients_count", 0),
            additives_count=data.get("additives_count", 0),
            nova_group=data.get("nova_group", 0),
            nutriscore=data.get("nutriscore", ""),
            nutriments=Nutriments(**data.get("nutriments", {})),
            labels=data.get("labels", []),
            packaging=Packaging(**data.get("packaging", {})),
            origin=data.get("origin", ""),
            countries=data.get("countries", []),
            image_front_url=data.get("image_front_url", "")
        )
    
    @classmethod
    def from_openfoodfacts(cls, data: dict) -> "NormalizedProductData":
        """
        Extract and normalize ONLY the required fields from OpenFoodFacts.
        
        This normalization is critical for:
        - Ingredients, NOVA, additives → trust & ultra-processing risk
        - Proteins, fibers, salt → value vs price perception
        - Packaging materials → greenwashing risk
        - Category → expected plant-based standards
        """
        product = data.get("product", data)
        
        # Derive plant-based category
        categories = product.get("categories_tags", [])
        plant_based_category = _derive_plant_based_category(categories)
        
        # Count ingredients
        ingredients_list = product.get("ingredients", [])
        ingredients_count = len(ingredients_list) if isinstance(ingredients_list, list) else 0
        
        # Count additives
        additives_tags = product.get("additives_tags", [])
        additives_count = len(additives_tags) if isinstance(additives_tags, list) else 0
        
        # Extract clean labels
        labels_tags = product.get("labels_tags", [])
        labels = _normalize_labels(labels_tags)
        
        # Extract clean countries
        countries_tags = product.get("countries_tags", [])
        countries = [c.replace("en:", "").replace("fr:", "") for c in countries_tags]
        
        return cls(
            product_id=product.get("code", ""),
            name=product.get("product_name", "") or product.get("product_name_en", ""),
            brand=product.get("brands", ""),
            plant_based_category=plant_based_category,
            ingredients_text=product.get("ingredients_text", "") or product.get("ingredients_text_en", ""),
            ingredients_count=ingredients_count,
            additives_count=additives_count,
            nova_group=int(product.get("nova_group", 0) or 0),
            nutriscore=(product.get("nutriscore_grade", "") or "").upper(),
            nutriments=Nutriments.from_openfoodfacts(product.get("nutriments", {})),
            labels=labels,
            packaging=Packaging.from_openfoodfacts(product),
            origin=product.get("origins", "") or product.get("origin", ""),
            countries=countries,
            image_front_url=product.get("image_front_url", "") or product.get("image_url", "")
        )


def _derive_plant_based_category(categories_tags: List[str]) -> str:
    """Derive the most relevant plant-based category from categories_tags."""
    categories_lower = [c.lower().replace("en:", "").replace("fr:", "") for c in categories_tags]
    
    # Priority mapping for plant-based categories
    priority_categories = [
        ("meat-alternatives", "meat-alternative"),
        ("dairy-alternatives", "dairy-alternative"),
        ("plant-milks", "plant-milk"),
        ("plant-based-foods", "plant-based"),
        ("vegan", "vegan"),
        ("vegetarian", "vegetarian"),
        ("tofu", "tofu"),
        ("tempeh", "tempeh"),
        ("seitan", "seitan"),
        ("legumes", "legumes"),
        ("plant-proteins", "plant-protein"),
        ("soy", "soy-based"),
        ("oat", "oat-based"),
        ("almond", "almond-based"),
        ("coconut", "coconut-based")
    ]
    
    for keyword, category in priority_categories:
        for cat in categories_lower:
            if keyword in cat:
                return category
    
    # Fallback: check for any plant-based indicator
    for cat in categories_lower:
        for pb_cat in PLANT_BASED_CATEGORIES:
            if pb_cat in cat:
                return pb_cat
    
    return "unknown"


def _normalize_labels(labels_tags: List[str]) -> List[str]:
    """Normalize labels to clean, relevant list."""
    relevant_labels = [
        "organic", "bio", "vegan", "vegetarian", "gluten-free", 
        "no-additives", "no-preservatives", "non-gmo", "fair-trade",
        "palm-oil-free", "sustainable", "eco-friendly", "local"
    ]
    
    normalized = []
    for tag in labels_tags:
        tag_clean = tag.lower().replace("en:", "").replace("fr:", "")
        for label in relevant_labels:
            if label in tag_clean and label not in normalized:
                normalized.append(label)
    
    return normalized


# =============================================================================
# IMAGE ANALYSIS RESULT
# =============================================================================

@dataclass
class ImageAnalysisResult:
    """
    Result from GPT Vision analysis of product packaging.
    
    Contains:
    - Detailed observations with visual evidence
    - Detected problems with severity and visual proof
    - Clear textual description of current packaging
    - Specific, actionable improvement proposals with full context
    """
    image_description: str = ""
    observations: List[str] = field(default_factory=list)
    problemes_detectes: List[Dict[str, str]] = field(default_factory=list)
    attractiveness_improvements: List[Any] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_description": self.image_description,
            "observations": self.observations,
            "problemes_detectes": self.problemes_detectes,
            "attractiveness_improvements": self.attractiveness_improvements
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImageAnalysisResult":
        return cls(
            image_description=data.get("image_description", ""),
            observations=data.get("observations", []),
            problemes_detectes=data.get("problemes_detectes", []),
            attractiveness_improvements=data.get("attractiveness_improvements", [])
        )
    
    @classmethod
    def empty(cls) -> "ImageAnalysisResult":
        return cls(
            image_description="No image available for analysis",
            observations=[],
            problemes_detectes=[],
            attractiveness_improvements=[]
        )


# =============================================================================
# OPENFOODFACTS CLIENT
# =============================================================================

class OpenFoodFactsClient:
    """Client for OpenFoodFacts API with plant-based normalization."""
    
    BASE_URL = "https://world.openfoodfacts.org/api/v2"
    
    def __init__(self, user_agent: str = "PlantBasedIntelligence/1.0"):
        self.user_agent = user_agent
    
    def get_product_by_barcode(self, barcode: str) -> Optional[NormalizedProductData]:
        """Fetch and normalize product data by barcode."""
        url = f"{self.BASE_URL}/product/{barcode}.json"
        
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": self.user_agent}
            )
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                
                if data.get("status") == 1:
                    return NormalizedProductData.from_openfoodfacts(data)
                else:
                    return None
        except Exception as e:
            print(f"Error fetching product {barcode}: {e}")
            return None
    
    def search_plant_based(self, query: str, page: int = 1, page_size: int = 20) -> List[NormalizedProductData]:
        """Search for plant-based products."""
        params = urllib.parse.urlencode({
            "search_terms": query,
            "tagtype_0": "categories",
            "tag_contains_0": "contains",
            "tag_0": "plant-based",
            "page": page,
            "page_size": page_size,
            "json": 1
        })
        url = f"https://world.openfoodfacts.org/cgi/search.pl?{params}"
        
        try:
            request = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                
                products = []
                for product_data in data.get("products", []):
                    products.append(NormalizedProductData.from_openfoodfacts({"product": product_data}))
                return products
        except Exception as e:
            print(f"Error searching products: {e}")
            return []


# =============================================================================
# GPT VISION IMAGE ANALYZER
# =============================================================================

class ImageAnalyzer:
    """
    Analyzes product packaging images using GPT Vision API.
    
    Generates:
    1. Clear textual description of current packaging
    2. Specific, actionable improvement proposals for:
       - Increasing perceived attractiveness
       - Reducing ultra-processed/greenwashing perception
       - Better communicating plant-based value
    """
    
    VISION_PROMPT = """Tu es un ***expert en amélioration d'images*** de packaging alimentaire.

{{RÈGLES STRICTES}}:
- ***Aucun conseil générique*** (ex: "améliorer la qualité", "rendre plus pro") sans détail opérationnel.
- Base-toi ***uniquement*** sur des éléments visibles dans l'image.
- Si une info manque, dis-le explicitement avec {{[Info manquante]}}.
- Pour chaque recommandation: précise le ***problème observé***, la ***preuve visuelle***, l'***action exacte***, et le ***résultat attendu***.
- Ajoute un tag {{[Applicable]}} ou {{[Non applicable]}} selon ce que l'image permet d'affirmer.

{{ANALYSE REQUISE}}:

***1. OBSERVATIONS*** (bullets détaillées):
- Style visuel et qualité du design (police, hiérarchie, alignement)
- Palette de couleurs et harmonie chromatique
- Claims et certifications visibles (bio, vegan, etc.)
- Indices végétaux et positionnement naturel
- Clarté de la proposition de valeur
- Présence en rayon et impact visuel
- Matériaux d'emballage visibles

***2. PROBLÈMES DÉTECTÉS*** (avec indices visuels):
- Chaque problème doit citer un élément visible précis
- Évaluer l'impact sur: attractivité, perception ultra-transformé, greenwashing
- Prioriser par gravité (Critique / Important / Mineur)

***3. RECOMMANDATIONS ACTIONNABLES***:
Pour chaque recommandation fournir:
- {{Problème}}: Description précise du problème observé
- {{Preuve visuelle}}: Élément visible qui justifie ce constat
- {{Action exacte}}: Modification spécifique à effectuer (outils/paramètres si possible)
- {{Résultat attendu}}: Bénéfice concret pour le consommateur/la marque
- {{Applicabilité}}: [Applicable] ou [Non applicable]

{{FORMAT DE SORTIE JSON}}:
{
  "observations": [
    "observation détaillée 1 avec élément visuel cité",
    "observation détaillée 2 avec élément visuel cité"
  ],
  "problemes_detectes": [
    {
      "probleme": "description du problème",
      "indice_visuel": "élément visible qui le prouve",
      "gravite": "Critique|Important|Mineur",
      "impact": "attractivité|ultra-transformé|greenwashing"
    }
  ],
  "image_description": "description synthétique du packaging actuel",
  "attractiveness_improvements": [
    {
      "probleme": "problème observé",
      "preuve_visuelle": "élément visible",
      "action_exacte": "modification spécifique avec détails techniques si possible",
      "resultat_attendu": "bénéfice concret",
      "applicabilite": "[Applicable]"
    }
  ]
}

***IMPORTANT***: Ne jamais inventer d'éléments non visibles. Rester factuel et actionnable."""

    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self._client = None
    
    def _get_client(self):
        """Lazy initialization of OpenAI client."""
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai package required for image analysis")
        return self._client
    
    def analyze_from_url(self, image_url: str) -> ImageAnalysisResult:
        """Analyze packaging image from URL using GPT Vision.
        
        Downloads the image locally first, then sends it as base64 to avoid
        OpenAI Vision API timeout issues when downloading from external URLs.
        """
        if not image_url:
            return ImageAnalysisResult.empty()
        
        if not self.api_key:
            # Return placeholder if no API key
            return ImageAnalysisResult(
                image_description=f"Image available at: {image_url} (Vision API key required for analysis)",
                attractiveness_improvements=["Enable GPT Vision API for detailed packaging analysis"]
            )
        
        try:
            # Download image locally first to avoid Vision API timeout
            print(f"   Downloading image from {image_url}...")
            request = urllib.request.Request(
                image_url,
                headers={"User-Agent": "PlantBasedIntelligence/1.0"}
            )
            
            # Download with timeout and retry logic
            max_retries = 3
            retry_delay = 2
            image_data = None
            
            for attempt in range(max_retries):
                try:
                    with urllib.request.urlopen(request, timeout=30) as response:
                        image_data = response.read()
                        break
                except Exception as download_error:
                    if attempt < max_retries - 1:
                        print(f"   Download attempt {attempt + 1} failed, retrying in {retry_delay}s...")
                        import time
                        time.sleep(retry_delay)
                    else:
                        raise download_error
            
            if not image_data:
                raise Exception("Failed to download image after retries")
            
            # Encode to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Determine media type from URL
            media_type = "image/jpeg"
            if image_url.lower().endswith('.png'):
                media_type = "image/png"
            elif image_url.lower().endswith('.webp'):
                media_type = "image/webp"
            
            print(f"   Image downloaded successfully ({len(image_data)} bytes), sending to Vision API...")
            
            # Now send to Vision API as base64
            client = self._get_client()
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.VISION_PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON from response
            return self._parse_vision_response(content)
            
        except Exception as e:
            print(f"Vision API error: {e}")
            print(f"   Continuing without image analysis...")
            return ImageAnalysisResult(
                image_description=f"Image analysis failed: {str(e)}",
                attractiveness_improvements=[]
            )
    
    def analyze_from_base64(self, image_data: str, media_type: str = "image/jpeg") -> ImageAnalysisResult:
        """Analyze packaging image from base64 data."""
        if not self.api_key:
            return ImageAnalysisResult.empty()
        
        try:
            client = self._get_client()
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.VISION_PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            return self._parse_vision_response(content)
            
        except Exception as e:
            print(f"Vision API error: {e}")
            return ImageAnalysisResult(
                image_description=f"Image analysis failed: {str(e)}",
                attractiveness_improvements=[]
            )
    
    def _parse_vision_response(self, content: str) -> ImageAnalysisResult:
        """Parse GPT Vision response into structured result with enhanced format."""
        import re
        
        # Try to extract JSON
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return ImageAnalysisResult(
                    image_description=data.get("image_description", ""),
                    observations=data.get("observations", []),
                    problemes_detectes=data.get("problemes_detectes", []),
                    attractiveness_improvements=data.get("attractiveness_improvements", [])
                )
            except json.JSONDecodeError:
                pass
        
        # Fallback: use content as description
        return ImageAnalysisResult(
            image_description=content,
            observations=[],
            problemes_detectes=[],
            attractiveness_improvements=[]
        )
    
    def manual_input(
        self,
        image_description: str = "",
        attractiveness_improvements: List[str] = None
    ) -> ImageAnalysisResult:
        """Create analysis from manual input."""
        return ImageAnalysisResult(
            image_description=image_description,
            attractiveness_improvements=attractiveness_improvements or []
        )


# =============================================================================
# SAMPLE DATA FOR TESTING
# =============================================================================

def create_sample_product_data() -> NormalizedProductData:
    """Create sample plant-based product for testing."""
    return NormalizedProductData(
        product_id="3760020507350",
        name="Beyond Burger Plant-Based Patties",
        brand="Beyond Meat",
        plant_based_category="meat-alternative",
        ingredients_text="Water, pea protein, expeller-pressed canola oil, refined coconut oil, rice protein, natural flavors, cocoa butter, mung bean protein, methylcellulose, potato starch, apple extract, pomegranate extract, salt, potassium chloride, vinegar, lemon juice concentrate, sunflower lecithin, beet juice extract",
        ingredients_count=18,
        additives_count=2,
        nova_group=4,
        nutriscore="C",
        nutriments=Nutriments(
            proteins_100g=18.0,
            fiber_100g=2.0,
            salt_100g=1.1,
            sugars_100g=0.5
        ),
        labels=["vegan", "non-gmo", "gluten-free"],
        packaging=Packaging(materials=["plastic", "cardboard"], recyclable=True),
        origin="United States",
        countries=["france", "germany", "united-states"],
        image_front_url="https://images.openfoodfacts.org/images/products/376/002/050/7350/front_en.jpg"
    )


def create_sample_image_analysis() -> ImageAnalysisResult:
    """Create sample image analysis for testing."""
    return ImageAnalysisResult(
        image_description="Modern packaging with green and brown earth tones. Features prominent 'PLANT-BASED' claim and protein content callout. Burger patty image looks realistic. Clean sans-serif typography. Recyclable symbol visible. Overall premium positioning with strong plant-based messaging.",
        attractiveness_improvements=[
            "Add visible 'high protein' badge to communicate nutritional value at a glance",
            "Include natural ingredient imagery (peas, vegetables) to reduce ultra-processed perception",
            "Add third-party certification logos (Non-GMO, Vegan) more prominently for trust",
            "Consider matte finish instead of glossy to reinforce natural positioning",
            "Add QR code linking to sustainability story to address greenwashing concerns"
        ]
    )