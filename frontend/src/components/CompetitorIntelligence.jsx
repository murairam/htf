import React from 'react'
import Plot from 'react-plotly.js'

const MetricCard = ({ label, value, icon }) => (
  <div className="bg-gradient-to-br from-white to-gray-50 p-4 rounded-lg border-2 border-gray-200 shadow-md hover:shadow-lg transition-shadow">
    <div className="flex items-center justify-between mb-2">
      <span className="text-sm font-semibold text-gray-600">{label}</span>
      {icon && <span className="text-2xl">{icon}</span>}
    </div>
    <div className="text-2xl font-bold text-gray-900">{value}</div>
  </div>
)

const CompetitorsTable = ({ competitors }) => {
  if (!competitors || competitors.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No competitor data available
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white border-2 border-gray-200 rounded-lg overflow-hidden">
        <thead className="bg-gradient-to-r from-blue-50 to-indigo-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
              Company
            </th>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
              Product
            </th>
            <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
              Price (€/kg)
            </th>
            <th className="px-4 py-3 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
              CO₂ (kg)
            </th>
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
              Marketing Claim
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {competitors.map((competitor, index) => (
            <tr key={index} className="hover:bg-gray-50 transition-colors">
              <td className="px-4 py-3 text-sm font-medium text-gray-900">
                {competitor.company || 'N/A'}
              </td>
              <td className="px-4 py-3 text-sm text-gray-700">
                {competitor.product || 'N/A'}
              </td>
              <td className="px-4 py-3 text-sm text-right font-semibold text-green-600">
                €{competitor.price_per_kg?.toFixed(2) || 'N/A'}
              </td>
              <td className="px-4 py-3 text-sm text-right font-semibold text-orange-600">
                {competitor.co2_emission_kg?.toFixed(2) || 'N/A'}
              </td>
              <td className="px-4 py-3 text-sm text-gray-600">
                {competitor.marketing_claim || 'N/A'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

const CompetitorIntelligence = ({ data }) => {
  if (!data) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg">No competitor intelligence data available</p>
        <p className="text-sm mt-2">This data comes from EssenceAI analysis</p>
      </div>
    )
  }

  const { metrics, competitors, visualizations } = data

  return (
    <div className="space-y-6">
      {/* Metrics Cards */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Avg Price/kg"
            value={`€${metrics.avg_price_per_kg?.toFixed(2) || '0.00'}`}
            icon="💰"
          />
          <MetricCard
            label="Avg CO₂/kg"
            value={`${metrics.avg_co2_emission?.toFixed(2) || '0.00'} kg`}
            icon="🌱"
          />
          <MetricCard
            label="Competitors"
            value={metrics.competitor_count || 0}
            icon="🏢"
          />
          <MetricCard
            label="Price Range"
            value={`€${metrics.price_range?.min?.toFixed(2) || '0'}-€${metrics.price_range?.max?.toFixed(2) || '0'}`}
            icon="📊"
          />
        </div>
      )}

      {/* Competitors Table */}
      {competitors && competitors.length > 0 && (
        <div className="card card-elevated">
          <h3 className="text-lg font-bold mb-4 text-gray-900">Competitor Overview</h3>
          <CompetitorsTable competitors={competitors} />
        </div>
      )}

      {/* Visualizations */}
      {visualizations && (
        <div className="space-y-6">
          {/* Price Chart */}
          {visualizations.price_chart && visualizations.price_chart.data && (
            <div className="card card-elevated">
              <Plot
                data={visualizations.price_chart.data}
                layout={{
                  ...visualizations.price_chart.layout,
                  autosize: true,
                  responsive: true
                }}
                useResizeHandler={true}
                style={{ width: '100%', height: '400px' }}
                config={{ displayModeBar: true, responsive: true }}
              />
            </div>
          )}

          {/* CO2 Chart */}
          {visualizations.co2_chart && visualizations.co2_chart.data && (
            <div className="card card-elevated">
              <Plot
                data={visualizations.co2_chart.data}
                layout={{
                  ...visualizations.co2_chart.layout,
                  autosize: true,
                  responsive: true
                }}
                useResizeHandler={true}
                style={{ width: '100%', height: '400px' }}
                config={{ displayModeBar: true, responsive: true }}
              />
            </div>
          )}

          {/* Scatter Chart */}
          {visualizations.scatter_chart && visualizations.scatter_chart.data && (
            <div className="card card-elevated">
              <Plot
                data={visualizations.scatter_chart.data}
                layout={{
                  ...visualizations.scatter_chart.layout,
                  autosize: true,
                  responsive: true
                }}
                useResizeHandler={true}
                style={{ width: '100%', height: '500px' }}
                config={{ displayModeBar: true, responsive: true }}
              />
            </div>
          )}
        </div>
      )}

      {/* Analysis Summary */}
      {data.analysis_summary && (
        <div className="card card-elevated">
          <h3 className="text-lg font-bold mb-3 text-gray-900">Analysis Summary</h3>
          <p className="text-gray-700">{data.analysis_summary}</p>
        </div>
      )}

      {/* Market Overview */}
      {data.market_overview && (
        <div className="card card-elevated">
          <h3 className="text-lg font-bold mb-3 text-gray-900">Market Overview</h3>
          <p className="text-gray-700">{data.market_overview}</p>
        </div>
      )}
    </div>
  )
}

export default CompetitorIntelligence
