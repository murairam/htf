import React, { useState } from 'react'
import Accordion from './Accordion'

/**
 * Generic recursive renderer for JSON data structures.
 * Handles objects, arrays, primitives, and nested structures.
 */
const KeyValueRenderer = ({ data, path = '', depth = 0, maxDepth = 5 }) => {
  // Humanize field names for better readability
  const humanizeKey = (key) => {
    // Special cases mapping
    const specialCases = {
      'product_information': 'Product Information',
      'basic_info': 'Basic Information',
      'ingredients_text': 'Ingredients',
      'ingredients_count': 'Number of Ingredients',
      'additives_count': 'Number of Additives',
      'nova_group': 'NOVA Group (Processing Level)',
      'nutriscore': 'Nutri-Score',
      'nutriments': 'Nutritional Values',
      'labels_certifications': 'Labels & Certifications',
      'scoring_results': 'Scoring Results',
      'evidence_based_explanations': 'Evidence-Based Explanations',
      'swot_analysis': 'SWOT Analysis',
      'packaging_improvements': 'Packaging Improvements',
      'go_to_market_strategy': 'Go-to-Market Strategy',
      'quality_insights': 'Quality Insights',
      'competitor_intelligence': 'Competitor Intelligence',
      'marketing_strategy_essence': 'Marketing Strategy',
      'research_insights_essence': 'Research Insights',
      'attractiveness_score': 'Attractiveness Score',
      'utility_score': 'Utility Score',
      'positioning_score': 'Positioning Score',
      'global_score': 'Global Score',
      'shelf_positioning': 'Shelf Positioning',
      'b2b_targeting': 'B2B Targeting',
      'regional_relevance': 'Regional Relevance',
      'reflector_analysis': 'Reflector Analysis',
      'key_insights': 'Key Insights',
      'improvement_guidelines': 'Improvement Guidelines',
      'proteins_100g': 'Proteins (per 100g)',
      'fiber_100g': 'Fiber (per 100g)',
      'salt_100g': 'Salt (per 100g)',
      'sugars_100g': 'Sugars (per 100g)'
    }
    
    if (specialCases[key]) {
      return specialCases[key]
    }
    
    // General transformation: snake_case to Title Case
    return key
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  // Prevent infinite recursion
  if (depth > maxDepth) {
    return <span className="text-gray-400 text-sm">[Max depth reached]</span>
  }

  // Handle null/undefined
  if (data === null || data === undefined) {
    return <span className="text-gray-400 italic">null</span>
  }

  // Handle primitives
  if (typeof data !== 'object') {
    if (typeof data === 'string' && data.length > 200) {
      // Long strings - show preview with expand option
      const [expanded, setExpanded] = useState(false)
      return (
        <div>
          {expanded ? (
            <div>
              <pre className="text-sm bg-gray-50 p-2 rounded whitespace-pre-wrap">{data}</pre>
              <button
                onClick={() => setExpanded(false)}
                className="text-xs text-blue-600 hover:underline mt-1"
              >
                Show less
              </button>
            </div>
          ) : (
            <div>
              <span className="text-sm">{data.substring(0, 200)}...</span>
              <button
                onClick={() => setExpanded(true)}
                className="text-xs text-blue-600 hover:underline ml-2"
              >
                Show more
              </button>
            </div>
          )}
        </div>
      )
    }
    
    // Format numbers nicely
    if (typeof data === 'number') {
      return <span className="text-sm font-medium text-gray-900">{data}</span>
    }
    
    // Format booleans
    if (typeof data === 'boolean') {
      return (
        <span className={`text-sm font-medium ${data ? 'text-green-600' : 'text-red-600'}`}>
          {data ? 'Yes' : 'No'}
        </span>
      )
    }
    
    return <span className="text-sm text-gray-700">{String(data)}</span>
  }

  // Handle arrays
  if (Array.isArray(data)) {
    if (data.length === 0) {
      return <span className="text-gray-400 text-sm italic">[Empty array]</span>
    }

    return (
      <div className="space-y-2">
        {data.map((item, index) => (
          <div key={index} className="border-l-2 border-blue-200 pl-3">
            <div className="text-xs text-gray-500 mb-1">Item {index + 1}</div>
            <KeyValueRenderer
              data={item}
              path={`${path}[${index}]`}
              depth={depth + 1}
              maxDepth={maxDepth}
            />
          </div>
        ))}
      </div>
    )
  }

  // Handle objects
  const keys = Object.keys(data)
  if (keys.length === 0) {
    return <span className="text-gray-400 text-sm italic">[Empty object]</span>
  }

  // For nested objects, use accordion for better UX
  if (depth > 0 && keys.length > 3) {
    return (
      <Accordion
        title={`${keys.length} fields`}
        defaultOpen={depth < 2}
      >
        <div className="space-y-3 mt-2">
          {keys.map((key) => (
            <div key={key} className="border-b border-gray-100 pb-2 last:border-0">
              <div className="font-semibold text-sm text-gray-800 mb-1">
                {humanizeKey(key)}
              </div>
              <div className="ml-2">
                <KeyValueRenderer
                  data={data[key]}
                  path={path ? `${path}.${key}` : key}
                  depth={depth + 1}
                  maxDepth={maxDepth}
                />
              </div>
            </div>
          ))}
        </div>
      </Accordion>
    )
  }

  // For shallow objects or at root level, show inline
  return (
    <div className="space-y-3">
      {keys.map((key) => (
        <div key={key} className="border-b border-gray-100 pb-2 last:border-0">
          <div className="font-semibold text-sm text-gray-800 mb-1">
            {humanizeKey(key)}
          </div>
          <div className="ml-2">
            <KeyValueRenderer
              data={data[key]}
              path={path ? `${path}.${key}` : key}
              depth={depth + 1}
              maxDepth={maxDepth}
            />
          </div>
        </div>
      ))}
    </div>
  )
}

export default KeyValueRenderer

