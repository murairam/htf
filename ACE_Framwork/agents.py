"""
ACE Plant-Based Packaging Intelligence agents and pipeline.

Contains system prompts and pipeline implementation for Generator, Reflector, and Curator
focused on plant-based product perception, trust, and go-to-market decisions.

IMPORTANT: Internal agents and playbook content are NEVER exposed to end users.
"""
import json
from typing import Dict, Any, Optional

from config import ACEConfig
from llm_client import create_client
from playbook import PlaybookManager

# =============================================================================
# GENERATOR PROMPT - Plant-Based Packaging Intelligence Analysis
# =============================================================================

GENERATOR_SYSTEM_PROMPT = """You are a ***strict scoring engine*** for plant-based food packaging evaluation.

{{IMPORTANT RULES}}:
- You must ***NOT*** predict sales or market success.
- You must ***NOT*** invent facts not visible on the packaging or not provided in context.
- You must follow the ***scoring rubric EXACTLY***.
- You must output ***ONLY valid JSON*** (no prose).
- All criterion values must be one of the ***allowed choices***.
- Scores ***MUST*** be consistent with the criterion values and the rubric.

{{TARGET AUDIENCE}}:
- Flexitarians and plant-curious consumers.

{{CONTEXT PROVIDED}}:
- Business Objective (one of): ["reduce_upf_perception", "launch_in_gms", "reposition_brand", "increase_flexitarian_appeal"]
- Product Data: normalized product information (ingredients, NOVA, additives, nutrients, packaging, labels)
- Image Analysis: packaging description and visual observations
- Playbook: accumulated domain knowledge (between ***PLAYBOOK_BEGIN*** and ***PLAYBOOK_END***)

{{TASK}}:
1) Analyze the product data and image analysis to fill the criterion fields using ***ONLY allowed values***.
2) Convert each criterion to points using the rubric.
3) Compute the three subscores (0–100).
4) Compute the ***global score*** using the objective weights.
5) Provide short, ***evidence-based explanations***: each explanation must cite a visible packaging element or product data.
6) Provide packaging improvement proposals and go-to-market recommendations.

{{SCORING RUBRIC}} (***DO NOT DEVIATE***):

***A) ATTRACTIVENESS (0–100)***
Criteria and points:
1. readability: {{"yes"}}=1, {{"partially"}}=0.5, {{"no"}}=0
2. visual_simplicity: {{"simple"}}=1, {{"moderate"}}=0.5, {{"overloaded"}}=0
3. naturalness_cues: {{"clear"}}=1, {{"weak"}}=0.5, {{"none"}}=0
4. familiarity: {{"familiar"}}=1, {{"somewhat familiar"}}=0.5, {{"unfamiliar"}}=0
***Attractiveness_score = average(points of 4 criteria) × 100***

***B) UTILITY (0–100)***
Criteria and points:
1. benefit_clarity: {{"clear"}}=1, {{"partially clear"}}=0.5, {{"unclear"}}=0
2. usage_clarity: {{"clear"}}=1, {{"partially clear"}}=0.5, {{"unclear"}}=0
3. ingredients_promise_coherence: {{"coherent"}}=1, {{"partially coherent"}}=0.5, {{"not coherent"}}=0
4. message_focus: {{"focused"}}=1, {{"somewhat scattered"}}=0.5, {{"scattered"}}=0
***Utility_score = average(points of 4 criteria) × 100***

***C) POSITIONING COHERENCE (0–100)***
Criteria and points:
1. positioning_clarity: {{"clear"}}=1, {{"somewhat clear"}}=0.5, {{"unclear"}}=0
2. tone_consistency: {{"consistent"}}=1, {{"partially consistent"}}=0.5, {{"inconsistent"}}=0
3. greenwashing_risk: {{"low"}}=1, {{"moderate"}}=0.5, {{"high"}}=0
***Positioning_score = average(points of 3 criteria) × 100***

{{ADDITIONAL SCORING FACTORS FROM PRODUCT DATA}}:
- NOVA group: 1-2 = ***+5*** to utility, 3 = 0, 4 = ***-10*** to utility
- Additives count: 0 = ***+5*** to positioning, 1-3 = 0, 4+ = ***-5*** to positioning
- Protein per 100g: >15g = ***+5*** to utility, 10-15g = ***+2***, <10g = 0
- Fiber per 100g: >5g = ***+3*** to utility
- Labels (organic, vegan, etc.): each trusted label = ***+2*** to positioning (max +10)
- Packaging recyclable: yes = ***+5*** to positioning, no = ***-5*** to positioning

{{CONFIDENCE}} (does not change scores, only flags reliability):
confidence must be one of: {{"high"}}, {{"medium"}}, {{"low"}}

{{GLOBAL SCORE CALCULATION}}:
Use ***objective weights***:
- ***reduce_upf_perception***: attractiveness {{0.20}}, utility {{0.40}}, positioning {{0.40}}
- ***launch_in_gms***: attractiveness {{0.40}}, utility {{0.30}}, positioning {{0.30}}
- ***reposition_brand***: attractiveness {{0.30}}, utility {{0.30}}, positioning {{0.40}}
- ***increase_flexitarian_appeal***: attractiveness {{0.45}}, utility {{0.35}}, positioning {{0.20}}

If objective doesn't match, use default: attractiveness {{0.33}}, utility {{0.34}}, positioning {{0.33}}

***Global_score = (attractiveness_score × wA) + (utility_score × wU) + (positioning_score × wP)***
Apply score modifiers from product data, then ***cap between 0-100***.

OUTPUT JSON ONLY, with this exact structure:

{
  "objective": "the business objective used",
  "criteria": {
    "attractiveness": {
      "readability": "",
      "visual_simplicity": "",
      "naturalness_cues": "",
      "familiarity": ""
    },
    "utility": {
      "benefit_clarity": "",
      "usage_clarity": "",
      "ingredients_promise_coherence": "",
      "message_focus": ""
    },
    "positioning": {
      "positioning_clarity": "",
      "tone_consistency": "",
      "greenwashing_risk": ""
    }
  },
  "scores": {
    "attractiveness_score": 0,
    "utility_score": 0,
    "positioning_score": 0,
    "global_score": 0
  },
  "confidence": "",
  "explanations": {
    "attractiveness": ["evidence-based explanation 1", "evidence-based explanation 2"],
    "utility": ["evidence-based explanation 1", "evidence-based explanation 2"],
    "positioning": ["evidence-based explanation 1", "evidence-based explanation 2"],
    "global": ["summary of key factors affecting global score"]
  },
  "analysis": {
    "strengths": ["strength 1", "strength 2", "..."],
    "weaknesses": ["weakness 1", "weakness 2", "..."],
    "risks": ["risk 1", "risk 2", "..."]
  },
  "packaging_improvement_proposals": ["specific proposal 1", "specific proposal 2", "..."],
  "go_to_market_recommendations": {
    "shelf_positioning": "specific positioning advice based on scores and objective",
    "b2b_targeting": "B2B opportunity analysis if relevant",
    "regional_relevance": "regional market considerations"
  },
  "internal_reasoning": "detailed internal reasoning explaining score calculations and rubric application"
}

{{VALIDATION RULES}}:
- Scores must be numbers between ***0 and 100*** (integer or 1 decimal).
- If data is incomplete, set confidence={{"low"}} and choose ***conservative*** criterion values.
- ***Never*** mention playbook or internal processes in explanations.
- All explanations must cite ***specific product data or packaging elements***."""


def format_generator_user_message(
    playbook_text: str,
    product_data: dict,
    image_analysis: dict,
    business_objective: str
) -> str:
    """Format the user message for the Generator."""
    import json
    
    return f"""PLAYBOOK_BEGIN
{playbook_text}
PLAYBOOK_END

NORMALIZED_PRODUCT_DATA:
{json.dumps(product_data, indent=2, ensure_ascii=False)}

IMAGE_ANALYSIS:
{json.dumps(image_analysis, indent=2, ensure_ascii=False)}

BUSINESS_OBJECTIVE:
{business_objective}

Produce the plant-based packaging intelligence analysis as specified."""


# =============================================================================
# REFLECTOR PROMPT - Quality Audit & Learning Extraction
# =============================================================================

REFLECTOR_SYSTEM_PROMPT = """You are auditing an analysis of a ***plant-based food product***.

{{YOUR ROLE}}:
1. Critically evaluate the analysis quality and reasoning
2. Identify reasoning flaws, inconsistencies, or missed opportunities
3. Extract ***generalizable insights*** that could improve future analyses
4. Evaluate playbook knowledge usage (if any bullets were used)

{{COMPREHENSIVE AUDIT CHECKLIST}}:

***📊 SCORING CONSISTENCY***:
- Are scores (attractiveness, utility, positioning, global) justified by the data?
- Does NOVA group (1-4) appropriately impact utility score? (NOVA 4 = ultra-processed = ***lower utility***)
- Do additives count and ingredients count affect trust/utility perception?
- Is protein content reflected in utility score? (high protein = ***higher utility*** for plant-based)
- Does fiber content boost utility appropriately?
- Are salt/sugar levels considered as health risks?

***🌱 PLANT-BASED CATEGORY SPECIFICS***:
- Meat alternatives: Is protein >12g/100g recognized as strength? Price compared to meat?
- Dairy alternatives: Fortification and calcium mentioned? Taste/texture expectations?
- Plant milks: Sugar content (<5g good, >8g concern)? Environmental claims?
- Snacks/prepared: Clean label vs ultra-processed perception balance?

***📦 PACKAGING & PERCEPTION***:
- Are packaging materials assessed for greenwashing risk? (plastic without recyclable = ***red flag***)
- Does packaging clarity communicate plant-based value effectively?
- Are certifications (organic, vegan, etc.) properly valued?

***🎯 BUSINESS OBJECTIVE ALIGNMENT***:
- Did the analysis properly emphasize what the business objective requested?
- Are recommendations tailored to the stated objective?
- Should certain scores be weighted differently given the objective?

***💡 OPPORTUNITIES & PATTERNS***:
- What patterns emerged in this analysis that could be generalized?
- What scoring thresholds or rules became apparent?
- What product category insights should inform future analyses?
- What packaging or ingredient combinations create specific risks/opportunities?

{{BULLET EVALUATION}} - For each playbook bullet referenced (if any), evaluate as:
- {{"helpful"}}: correctly applied and improved the analysis
- {{"misused"}}: incorrectly applied or led to wrong conclusions  
- {{"irrelevant"}}: not applicable to this product

{{OUTPUT JSON}} (***MUST be valid JSON***):
{
  "analysis": "2-3 paragraph evaluation of the analysis quality - what was done well and what could improve",
  "identified_errors": "Specific mistakes, inconsistencies, or missed insights (or 'None' if analysis was solid)",
  "root_causes": "Why errors occurred - missing data consideration, wrong assumptions, category mismatch, etc.",
  "improved_reasoning_guidelines": "How to avoid similar errors - what to check, what thresholds to use, what patterns to recognize",
  "key_insights": "2-3 key generalizable insights from this analysis that could benefit future analyses",
  "bullet_evaluation": [
    {"id": "bullet-id", "tag": "helpful/misused/irrelevant"}
  ]
}

Be constructive and detailed. Your insights feed into the Curator to evolve the knowledge base.
Your output ***MUST be valid JSON***."""


def format_reflector_user_message(
    business_objective: str,
    product_data: dict,
    generator_output: dict,
    playbook_text: str,
    feedback: str = None
) -> str:
    """Format the user message for the Reflector."""
    import json
    
    parts = [
        f"BUSINESS_OBJECTIVE:\n{business_objective}",
        f"\nPRODUCT_DATA:\n{json.dumps(product_data, indent=2, ensure_ascii=False)}",
        f"\nANALYSIS_OUTPUT:\n{json.dumps(generator_output, indent=2, ensure_ascii=False)}",
        f"\nPLAYBOOK:\n{playbook_text}"
    ]
    
    if feedback:
        parts.append(f"\nEXTERNAL_FEEDBACK:\n{feedback}")
    
    parts.append("\nAudit the analysis and return your evaluation as JSON.")
    
    return "\n".join(parts)


# =============================================================================
# CURATOR PROMPT - Playbook Evolution
# =============================================================================

CURATOR_SYSTEM_PROMPT = """You are responsible for evolving the ***knowledge base*** for plant-based product analysis.

Based on the Reflector's audit and the analysis performed, extract ***GENERALIZABLE INSIGHTS*** that will improve future analyses.

Your goal is to ***CONTINUOUSLY LEARN*** and ***BUILD KNOWLEDGE***. Be proactive - every analysis should teach us something new.

{{PLAYBOOK SECTIONS}}:
- ***scoring_rules***: Rules for calculating or adjusting scores (formulas, thresholds, adjustments)
- ***plant_based_heuristics***: Plant-based specific decision guidelines (category patterns, consumer expectations)
- ***ultra_processing_pitfalls***: Common mistakes related to NOVA, additives, ingredients (clean label strategies)
- ***packaging_patterns***: Packaging-related insights and greenwashing detection (material choices, claims)
- ***go_to_market_rules***: Market positioning and targeting guidelines (channel strategies, pricing tiers)

{{WHEN TO ADD NEW KNOWLEDGE}}:
✅ ***YES*** - Add when you identify:
- New scoring patterns or thresholds that emerged from this analysis
- Product category insights (e.g., "meat alternatives vs plant milks behave differently")
- Packaging/ingredient combinations that create specific perception risks
- Business objective patterns that require different scoring emphasis
- Regional or channel-specific market behaviors
- Clean label vs ultra-processed perception triggers
- New greenwashing detection patterns

❌ ***NO*** - Don't add when:
- It's already covered in the existing playbook
- It's too product-specific (brand names, specific products)
- It's too vague to be actionable

{{QUALITY CRITERIA FOR NEW BULLETS}}:
1. ***GENERALIZABLE*** - Applies to multiple products, not just this one
2. ***ACTIONABLE*** - Can be directly applied in scoring or reasoning
3. ***UNIQUE*** - Adds new information not in current playbook
4. ***SPECIFIC*** - Contains concrete thresholds, patterns, or rules

{{EXCELLENT EXAMPLES}}:
- "scoring_rules: Products with NOVA 4 + >15 additives should cap utility score at {{45/100}} unless protein >18g/100g"
- "plant_based_heuristics: Meat alternatives targeting premium segment require protein >15g/100g for positioning coherence >{{70}}"
- "packaging_patterns: Non-recyclable plastic for plant-based products reduces attractiveness by ***10-20 points*** for eco-conscious positioning"
- "ultra_processing_pitfalls: Single-ingredient products with minimal processing justify utility scores >{{80}} regardless of low protein"
- "go_to_market_rules: B2B foodservice targeting requires emphasizing consistency and yield over taste claims"

{{OUTPUT JSON}} (***MUST be valid JSON***):
{
  "reasoning": "detailed explanation of what insights were extracted and why they're valuable",
  "operations": [
    {
      "type": "ADD",
      "section": "section_name",
      "content": "clear, generalizable, actionable rule with specific thresholds or patterns"
    }
  ]
}

{{IMPORTANT}}:
- Aim to extract ***1-3 valuable insights*** per analysis
- If you return empty operations, explain in reasoning why no new knowledge was needed
- ***NEVER*** remove or modify existing bullets - only ***ADD***
- Your output ***MUST be valid JSON***."""


def format_curator_user_message(
    business_objective: str,
    generator_output: dict,
    reflector_output: dict,
    playbook_text: str
) -> str:
    """Format the user message for the Curator."""
    import json
    
    return f"""BUSINESS_OBJECTIVE:
{business_objective}

ANALYSIS_OUTPUT:
{json.dumps(generator_output, indent=2, ensure_ascii=False)}

REFLECTOR_EVALUATION:
{json.dumps(reflector_output, indent=2, ensure_ascii=False)}

CURRENT_PLAYBOOK:
{playbook_text}

Determine what new knowledge should be added to the playbook."""


# =============================================================================
# OUTPUT STRUCTURE HELPERS
# =============================================================================

def get_empty_generator_response() -> dict:
    """Return an empty generator response structure."""
    return {
        "objective": "",
        "criteria": {
            "attractiveness": {
                "readability": "",
                "visual_simplicity": "",
                "naturalness_cues": "",
                "familiarity": ""
            },
            "utility": {
                "benefit_clarity": "",
                "usage_clarity": "",
                "ingredients_promise_coherence": "",
                "message_focus": ""
            },
            "positioning": {
                "positioning_clarity": "",
                "tone_consistency": "",
                "greenwashing_risk": ""
            }
        },
        "scores": {
            "attractiveness_score": 0,
            "utility_score": 0,
            "positioning_score": 0,
            "global_score": 0
        },
        "confidence": "low",
        "explanations": {
            "attractiveness": [],
            "utility": [],
            "positioning": [],
            "global": []
        },
        "analysis": {
            "strengths": [],
            "weaknesses": [],
            "risks": []
        },
        "packaging_improvement_proposals": [],
        "go_to_market_recommendations": {
            "shelf_positioning": "",
            "b2b_targeting": "",
            "regional_relevance": ""
        },
        "internal_reasoning": ""
    }


def get_empty_reflector_response() -> dict:
    """Return an empty reflector response structure."""
    return {
        "analysis": "",
        "identified_errors": "",
        "root_causes": "",
        "improved_reasoning_guidelines": "",
        "key_insights": "",
        "bullet_evaluation": []
    }


def get_empty_curator_response() -> dict:
    """Return an empty curator response structure."""
    return {
        "reasoning": "",
        "operations": []
    }


def sanitize_output_for_user(generator_output: dict) -> dict:
    """
    Remove internal fields before presenting to user.
    
    IMPORTANT: Playbook content and internal reasoning must never
    be exposed to end users.
    
    Note: For development/testing, we keep internal_reasoning visible.
    In production, uncomment the pop() lines below.
    """
    output = dict(generator_output)
    
    # Remove internal fields (commented out for development)
    # output.pop("internal_reasoning", None)
    # output.pop("used_bullet_ids", None)
    
    return output


# =============================================================================
# ACE PIPELINE
# =============================================================================

class ACEPipeline:
    """
    Main pipeline for ACE Plant-Based Packaging Intelligence analysis.
    
    Orchestrates Generator (analysis), Reflector (learning), and Curator (playbook updates).
    For the web interface, we primarily use just the Generator for fast analysis.
    """
    
    def __init__(self, config: ACEConfig):
        """Initialize the ACE pipeline."""
        self.config = config
        self.llm_client = create_client(config.llm)
        self.playbook_manager = PlaybookManager(config.playbook)
    
    def analyze(
        self,
        product_data: Dict[str, Any],
        image_analysis: Dict[str, Any],
        business_objective: str
    ) -> Dict[str, Any]:
        """
        Run Generator analysis only (fast mode for web interface).
        
        Args:
            product_data: Normalized product data
            image_analysis: Image analysis results
            business_objective: Business goal for the analysis
            
        Returns:
            Generator output dictionary with scores and recommendations
        """
        # Get playbook context
        playbook = self.playbook_manager.get_playbook()
        playbook_text = self._format_playbook_for_prompt(playbook)
        
        # Format prompt
        user_message = format_generator_user_message(
            playbook_text=playbook_text,
            product_data=product_data,
            image_analysis=image_analysis,
            business_objective=business_objective
        )
        
        # Call LLM
        response = self.llm_client.chat(
            system_prompt=GENERATOR_SYSTEM_PROMPT,
            user_message=user_message
        )
        
        # Parse response
        result = response.parse_json()
        if not result:
            # Fallback to empty response
            result = get_empty_generator_response()
        
        # Sanitize before returning to user
        return sanitize_output_for_user(result)
    
    def _format_playbook_for_prompt(self, playbook: Any) -> str:
        """Format playbook content for inclusion in prompts."""
        sections = []
        
        for section_name in ["scoring_rules", "heuristics", "pitfalls", "marketing_patterns", "packaging_patterns"]:
            bullets = playbook.get_section(section_name)
            if bullets:
                sections.append(f"## {section_name.upper().replace('_', ' ')}")
                for bullet in bullets:
                    sections.append(f"- {bullet.content}")
        
        return "\n".join(sections) if sections else "No accumulated knowledge yet."
    
    def get_playbook_stats(self) -> Dict[str, Any]:
        """Get playbook statistics."""
        playbook = self.playbook_manager.get_playbook()
        return playbook.get_stats()
    
    def get_playbook(self):
        """Get the playbook instance."""
        return self.playbook_manager.get_playbook()
    
    def run(
        self,
        product_data: Dict[str, Any],
        image_analysis: Dict[str, Any],
        business_objective: str,
        feedback: str = None
    ):
        """
        Run full pipeline with Generator, Reflector, and Curator.
        """
        # Step 1: Run Generator
        generator_output = self.analyze(product_data, image_analysis, business_objective)
        
        # Step 2: Run Reflector
        reflector_output = self._run_reflector(
            business_objective=business_objective,
            product_data=product_data,
            generator_output=generator_output,
            feedback=feedback
        )
        
        # Step 3: Run Curator
        curator_output, added_bullets = self._run_curator(
            business_objective=business_objective,
            generator_output=generator_output,
            reflector_output=reflector_output
        )
        
        # Create result object
        class Result:
            def __init__(self, gen_output, refl_output, cur_output, bullets):
                self.generator_output = type('obj', (object,), {
                    'scores': type('obj', (object,), gen_output.get('scores', {}))
                })()
                self._dict = {
                    "generator_output": gen_output,
                    "reflector_output": refl_output,
                    "curator_output": cur_output,
                    "added_bullets": bullets
                }
            
            def to_dict(self):
                return self._dict
        
        return Result(generator_output, reflector_output, curator_output, added_bullets)
    
    def _run_reflector(
        self,
        business_objective: str,
        product_data: Dict[str, Any],
        generator_output: Dict[str, Any],
        feedback: str = None
    ) -> Dict[str, Any]:
        """Run Reflector agent to audit the Generator's analysis."""
        try:
            # Get playbook context
            playbook = self.playbook_manager.get_playbook()
            playbook_text = self._format_playbook_for_prompt(playbook)
            
            # Format prompt
            user_message = format_reflector_user_message(
                business_objective=business_objective,
                product_data=product_data,
                generator_output=generator_output,
                playbook_text=playbook_text,
                feedback=feedback
            )
            
            # Call LLM
            response = self.llm_client.chat(
                system_prompt=REFLECTOR_SYSTEM_PROMPT,
                user_message=user_message
            )
            
            # Parse response
            result = response.parse_json()
            if not result:
                result = get_empty_reflector_response()
            
            return result
            
        except Exception as e:
            print(f"Reflector error: {e}")
            return get_empty_reflector_response()
    
    def _run_curator(
        self,
        business_objective: str,
        generator_output: Dict[str, Any],
        reflector_output: Dict[str, Any]
    ) -> tuple[Dict[str, Any], list]:
        """Run Curator agent to update the playbook."""
        try:
            # Get playbook context
            playbook = self.playbook_manager.get_playbook()
            playbook_text = self._format_playbook_for_prompt(playbook)
            
            # Format prompt
            user_message = format_curator_user_message(
                business_objective=business_objective,
                generator_output=generator_output,
                reflector_output=reflector_output,
                playbook_text=playbook_text
            )
            
            # Call LLM
            response = self.llm_client.chat(
                system_prompt=CURATOR_SYSTEM_PROMPT,
                user_message=user_message
            )
            
            # Parse response
            result = response.parse_json()
            if not result:
                result = get_empty_curator_response()
            
            # Apply operations to playbook using the manager's method
            operations = result.get("operations", [])
            added_bullets_objects = self.playbook_manager.apply_operations(operations)
            
            # Convert to serializable format
            added_bullets = []
            for bullet in added_bullets_objects:
                added_bullets.append({
                    "id": bullet.id,
                    "section": "",  # Section info not returned by apply_operations
                    "content": bullet.content
                })
            
            # Save playbook if changes were made
            if added_bullets:
                self.playbook_manager.save()
            
            return result, added_bullets
            
        except Exception as e:
            print(f"Curator error: {e}")
            return get_empty_curator_response(), []
    
    def generate_only(
        self,
        product_data: Dict[str, Any],
        image_analysis: Dict[str, Any],
        business_objective: str
    ):
        """
        Run only the Generator for quick analysis.
        
        Returns a simple wrapper object with the generator output.
        """
        generator_output = self.analyze(product_data, image_analysis, business_objective)
        
        class Output:
            def __init__(self, gen_output):
                self._dict = gen_output
            
            def to_dict(self):
                return self._dict
        
        return Output(generator_output)