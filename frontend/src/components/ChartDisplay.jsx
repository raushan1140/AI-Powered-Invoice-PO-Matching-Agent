import React from 'react';
import Plot from 'react-plotly.js';
import { BarChart3, PieChart, TrendingUp, Download } from 'lucide-react';

const ChartDisplay = ({ data, type, title, description }) => {
  if (!data || data.length === 0) {
    return (
      <div className="card">
        <div className="text-center py-8 text-gray-500">
          <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>No data available for chart</p>
        </div>
      </div>
    );
  }

  const getChartConfig = () => {
    switch (type) {
      case 'bar':
        return {
          data: [{
            x: data.map(item => item.label || item.name || item.vendor),
            y: data.map(item => item.value || item.score || item.total_spend),
            type: 'bar',
            marker: {
              color: '#3b82f6',
              opacity: 0.8
            }
          }],
          layout: {
            title: title,
            xaxis: { title: 'Categories' },
            yaxis: { title: 'Values' },
            margin: { t: 50, b: 50, l: 50, r: 50 },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)'
          }
        };

      case 'pie':
        return {
          data: [{
            values: data.map(item => item.value || item.count),
            labels: data.map(item => item.label || item.status || item.vendor),
            type: 'pie',
            marker: {
              colors: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
            }
          }],
          layout: {
            title: title,
            margin: { t: 50, b: 50, l: 50, r: 50 },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)'
          }
        };

      case 'line':
        return {
          data: [{
            x: data.map(item => item.date || item.label),
            y: data.map(item => item.value || item.count),
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#3b82f6' },
            marker: { color: '#3b82f6' }
          }],
          layout: {
            title: title,
            xaxis: { title: 'Time' },
            yaxis: { title: 'Values' },
            margin: { t: 50, b: 50, l: 50, r: 50 },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)'
          }
        };

      case 'scatter':
        return {
          data: [{
            x: data.map(item => item.x || item.validations_completed),
            y: data.map(item => item.y || item.score),
            mode: 'markers',
            type: 'scatter',
            marker: {
              size: 10,
              color: '#3b82f6',
              opacity: 0.7
            },
            text: data.map(item => item.team_name || item.label)
          }],
          layout: {
            title: title,
            xaxis: { title: 'X Axis' },
            yaxis: { title: 'Y Axis' },
            margin: { t: 50, b: 50, l: 50, r: 50 },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)'
          }
        };

      default:
        return {
          data: [],
          layout: { title: 'Unsupported chart type' }
        };
    }
  };

  const chartConfig = getChartConfig();

  const downloadChart = () => {
    // This would trigger a download of the chart as an image
    // Plotly.js supports this natively with toImage()
    const plot = document.querySelector('.js-plotly-plot');
    if (plot) {
      window.Plotly.toImage(plot, {
        format: 'png',
        width: 800,
        height: 600
      }).then(function(dataUrl) {
        const link = document.createElement('a');
        link.download = `${title.replace(/\s+/g, '_').toLowerCase()}.png`;
        link.href = dataUrl;
        link.click();
      });
    }
  };

  const getChartIcon = () => {
    switch (type) {
      case 'pie':
        return <PieChart className="h-5 w-5" />;
      case 'line':
        return <TrendingUp className="h-5 w-5" />;
      default:
        return <BarChart3 className="h-5 w-5" />;
    }
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center space-x-2 mb-1">
            {getChartIcon()}
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          </div>
          {description && (
            <p className="text-sm text-gray-600">{description}</p>
          )}
        </div>
        <button
          onClick={downloadChart}
          className="btn-secondary text-sm"
          title="Download chart as PNG"
        >
          <Download className="h-4 w-4 mr-1" />
          Download
        </button>
      </div>

      <div className="w-full h-96">
        <Plot
          data={chartConfig.data}
          layout={{
            ...chartConfig.layout,
            autosize: true,
            responsive: true
          }}
          config={{
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
            toImageButtonOptions: {
              format: 'png',
              filename: title.replace(/\s+/g, '_').toLowerCase(),
              height: 600,
              width: 800,
              scale: 1
            }
          }}
          style={{ width: '100%', height: '100%' }}
          useResizeHandler={true}
        />
      </div>

      {data.length > 0 && (
        <div className="mt-4 text-sm text-gray-500">
          <p>Data points: {data.length}</p>
        </div>
      )}
    </div>
  );
};

export default ChartDisplay;
