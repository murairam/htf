import React from 'react'

const ResearchInsightsACE = ({ data }) => {
  if (!data) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg">No ACE research insights data available</p>
      </div>
    )
  }

  const {
    consumer_trends,
    market_dynamics,
    nutritional_insights,
    sustainability_insights,
    innovation_opportunities,
    key_findings,
    summary,
    methodology
  } = data

  return (
    <div className="space-y-6">
      {/* Summary */}
      {summary && (
        <div className="card card-elevated bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200">
          <div className="flex items-start space-x-3">
            <span className="text-3xl">📊</span>
            <div className="flex-1">
              <h3 className="text-xl font-bold text-gray-900 mb-2">Research Summary</h3>
              <p className="text-gray-700 leading-relaxed">{summary}</p>
            </div>
          </div>
        </div>
      )}

      {/* Consumer Trends */}
      {consumer_trends && consumer_trends.length > 0 && (
        <div className="card card-elevated">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">📈</span>
            Consumer Trends
          </h3>
          <div className="space-y-3">
            {consumer_trends.map((trend, index) => (
              <div key={index} className="border-l-4 border-blue-500 pl-4 py-3 bg-blue-50 rounded-r-lg">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-semibold text-gray-900">{trend.trend}</h4>
                  <div className="flex gap-2">
                    {trend.impact && (
                      <span className={`text-xs px-2 py-1 rounded ${
                        trend.impact === 'High' ? 'bg-red-100 text-red-700' :
                        trend.impact === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        Impact: {trend.impact}
                      </span>
                    )}
                  </div>
                </div>
                <p className="text-sm text-gray-700 mb-2">{trend.description}</p>
                {trend.relevance && (
                  <p className="text-xs text-gray-600 italic">Relevance: {trend.relevance}</p>
                )}
                {trend.source && (
                  <p className="text-xs text-gray-500 mt-1">Source: {trend.source}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Market Dynamics */}
      {market_dynamics && Object.keys(market_dynamics).length > 0 && (
        <div className="card card-elevated bg-gradient-to-br from-purple-50 to-pink-50">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">🌍</span>
            Market Dynamics
          </h3>
          <div className="grid md:grid-cols-2 gap-4">
            {market_dynamics.market_size && (
              <div className="bg-white p-4 rounded-lg border-2 border-purple-200">
                <h4 className="text-sm font-semibold text-purple-700 mb-2">Market Size</h4>
                <p className="text-sm text-gray-700">{market_dynamics.market_size}</p>
              </div>
            )}
            {market_dynamics.growth_rate && (
              <div className="bg-white p-4 rounded-lg border-2 border-pink-200">
                <h4 className="text-sm font-semibold text-pink-700 mb-2">Growth Rate</h4>
                <p className="text-sm text-gray-700">{market_dynamics.growth_rate}</p>
              </div>
            )}
            {market_dynamics.competitive_landscape && (
              <div className="bg-white p-4 rounded-lg border-2 border-indigo-200">
                <h4 className="text-sm font-semibold text-indigo-700 mb-2">Competitive Landscape</h4>
                <p className="text-sm text-gray-700">{market_dynamics.competitive_landscape}</p>
              </div>
            )}
            {market_dynamics.price_trends && (
              <div className="bg-white p-4 rounded-lg border-2 border-blue-200">
                <h4 className="text-sm font-semibold text-blue-700 mb-2">Price Trends</h4>
                <p className="text-sm text-gray-700">{market_dynamics.price_trends}</p>
              </div>
            )}
            {market_dynamics.distribution_channels && (
              <div className="bg-white p-4 rounded-lg border-2 border-green-200 md:col-span-2">
                <h4 className="text-sm font-semibold text-green-700 mb-2">Distribution Channels</h4>
                <p className="text-sm text-gray-700">{market_dynamics.distribution_channels}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Nutritional Insights */}
      {nutritional_insights && Object.keys(nutritional_insights).length > 0 && (
        <div className="card card-elevated">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">🥗</span>
            Nutritional Insights
          </h3>
          <div className="grid md:grid-cols-2 gap-3">
            {nutritional_insights.protein_content && (
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-3 rounded-lg border border-green-200">
                <h4 className="text-sm font-semibold text-gray-900 mb-1">Protein Content</h4>
                <p className="text-xs text-gray-600">{nutritional_insights.protein_content}</p>
              </div>
            )}
            {nutritional_insights.fiber_content && (
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-3 rounded-lg border border-green-200">
                <h4 className="text-sm font-semibold text-gray-900 mb-1">Fiber Content</h4>
                <p className="text-xs text-gray-600">{nutritional_insights.fiber_content}</p>
              </div>
            )}
            {nutritional_insights.sodium_levels && (
              <div className="bg-gradient-to-br from-yellow-50 to-orange-50 p-3 rounded-lg border border-yellow-200">
                <h4 className="text-sm font-semibold text-gray-900 mb-1">Sodium Levels</h4>
                <p className="text-xs text-gray-600">{nutritional_insights.sodium_levels}</p>
              </div>
            )}
            {nutritional_insights.processing_level && (
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-3 rounded-lg border border-blue-200">
                <h4 className="text-sm font-semibold text-gray-900 mb-1">Processing Level</h4>
                <p className="text-xs text-gray-600">{nutritional_insights.processing_level}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Sustainability Insights */}
      {sustainability_insights && Object.keys(sustainability_insights).length > 0 && (
        <div className="card card-elevated bg-gradient-to-br from-green-50 to-teal-50">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">🌱</span>
            Sustainability Insights
          </h3>
          <div className="space-y-3">
            {sustainability_insights.carbon_footprint && (
              <div className="bg-white p-4 rounded-lg border-2 border-green-200">
                <h4 className="text-sm font-semibold text-green-700 mb-2">Carbon Footprint</h4>
                <p className="text-sm text-gray-700">{sustainability_insights.carbon_footprint}</p>
              </div>
            )}
            {sustainability_insights.water_usage && (
              <div className="bg-white p-4 rounded-lg border-2 border-blue-200">
                <h4 className="text-sm font-semibold text-blue-700 mb-2">Water Usage</h4>
                <p className="text-sm text-gray-700">{sustainability_insights.water_usage}</p>
              </div>
            )}
            {sustainability_insights.packaging_impact && (
              <div className="bg-white p-4 rounded-lg border-2 border-teal-200">
                <h4 className="text-sm font-semibold text-teal-700 mb-2">Packaging Impact</h4>
                <p className="text-sm text-gray-700">{sustainability_insights.packaging_impact}</p>
              </div>
            )}
            {sustainability_insights.consumer_perception && (
              <div className="bg-white p-4 rounded-lg border-2 border-emerald-200">
                <h4 className="text-sm font-semibold text-emerald-700 mb-2">Consumer Perception</h4>
                <p className="text-sm text-gray-700">{sustainability_insights.consumer_perception}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Innovation Opportunities */}
      {innovation_opportunities && innovation_opportunities.length > 0 && (
        <div className="card card-elevated">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">💡</span>
            Innovation Opportunities
          </h3>
          <div className="grid md:grid-cols-2 gap-4">
            {innovation_opportunities.map((opportunity, index) => (
              <div key={index} className="border-2 border-gray-200 rounded-lg p-4 hover:border-yellow-400 transition-colors">
                <h4 className="font-semibold text-gray-900 mb-2">{opportunity.opportunity}</h4>
                <p className="text-sm text-gray-600 mb-2">{opportunity.description}</p>
                {opportunity.potential_impact && (
                  <p className="text-xs text-gray-500">
                    <span className="font-semibold">Impact:</span> {opportunity.potential_impact}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Key Findings */}
      {key_findings && key_findings.length > 0 && (
        <div className="card card-elevated bg-gradient-to-r from-yellow-50 to-orange-50">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">🔑</span>
            Key Findings
          </h3>
          <ul className="space-y-2">
            {key_findings.map((finding, index) => (
              <li key={index} className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-orange-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  {index + 1}
                </span>
                <p className="text-sm text-gray-700 flex-1">{finding}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Methodology */}
      {methodology && (
        <div className="card card-elevated bg-gray-50">
          <h3 className="text-lg font-bold mb-4 text-gray-900 flex items-center">
            <span className="text-2xl mr-2">🔬</span>
            Methodology
          </h3>
          <p className="text-sm text-gray-700 leading-relaxed">{methodology}</p>
        </div>
      )}
    </div>
  )
}

export default ResearchInsightsACE
