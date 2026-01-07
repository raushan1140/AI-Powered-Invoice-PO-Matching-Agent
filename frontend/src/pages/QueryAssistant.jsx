import React, { useState, useEffect } from 'react';
import { BASE_URL } from '../config/api';
import { Search, Lightbulb, Clock, Database, Users, Code } from 'lucide-react';
import ResultsTable from '../components/ResultsTable';
import ChartDisplay from '../components/ChartDisplay';
import { API } from '../config/api';


const QueryAssistant = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [history, setHistory] = useState([]);
  const [teamId, setTeamId] = useState('');
  const [showSqlQuery, setShowSqlQuery] = useState(false);

  useEffect(() => {
    fetchSuggestions();
    fetchQueryHistory();
  }, []);

  const fetchSuggestions = async () => {
    try {
      const response = await fetch(`${API.QUERIES}/suggestions`);
      const data = await response.json();
      if (data.success) {
        setSuggestions(data.suggestions);
      }
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    }
  };

  const fetchQueryHistory = async () => {
    try {
      const response = await fetch(`${API.QUERIES}/history?limit=5`);
      const data = await response.json();
      if (data.success) {
        setHistory(data.history);
      }
    } catch (error) {
      console.error('Error fetching query history:', error);
    }
  };

  const executeQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setResults(null);

    try {
      const response = await fetch(`${API.QUERIES}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          team_id: teamId || undefined
        })
      });

      const data = await response.json();
      setResults(data);
      
      if (data.success) {
        fetchQueryHistory(); // Refresh history after successful query
      }
    } catch (error) {
      setResults({
        success: false,
        error: error.message
      });
    } finally {
      setLoading(false);
    }
  };

  const useSuggestion = (suggestion) => {
    setQuery(suggestion);
  };

  const useHistoryQuery = (historyItem) => {
    setQuery(historyItem.natural_language_query);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      executeQuery();
    }
  };

  const renderResults = () => {
    if (!results) return null;

    if (!results.success) {
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-sm font-medium text-red-800 mb-2">Query Error</h3>
          <p className="text-sm text-red-600">{results.error}</p>
          {results.suggestions && (
            <div className="mt-3">
              <p className="text-sm text-red-700 font-medium">Try these instead:</p>
              <ul className="mt-2 space-y-1">
                {results.suggestions.map((suggestion, index) => (
                  <li key={index}>
                    <button
                      onClick={() => useSuggestion(suggestion)}
                      className="text-sm text-red-600 hover:text-red-800 underline"
                    >
                      {suggestion}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      );
    }

    const chartData = results.results?.map((row, index) => ({
      label: row[Object.keys(row)[0]],
      value: row[Object.keys(row)[1]] || index,
      ...row
    }));

    const shouldShowChart = results.results && results.results.length > 0 && 
                           results.results.length <= 20 && 
                           Object.keys(results.results[0]).length >= 2;

    return (
      <div className="space-y-6">
        {/* Query Info */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-sm font-medium text-blue-800 mb-1">Query Executed Successfully</h3>
              <p className="text-sm text-blue-600">
                Found {results.result_count} results in {results.execution_time?.toFixed(3)}s
              </p>
              <p className="text-xs text-blue-500 mt-1">
                Method: {results.method === 'gpt4' ? 'GPT-4 Translation' : 'Pattern Matching'}
              </p>
            </div>
            <button
              onClick={() => setShowSqlQuery(!showSqlQuery)}
              className="btn-secondary text-xs"
            >
              <Code className="h-3 w-3 mr-1" />
              {showSqlQuery ? 'Hide SQL' : 'Show SQL'}
            </button>
          </div>
          
          {showSqlQuery && (
            <div className="mt-3 p-3 bg-gray-900 rounded text-green-400 text-sm font-mono">
              <pre className="whitespace-pre-wrap">{results.sql_query}</pre>
            </div>
          )}
        </div>

        {/* Results Table */}
        {results.results && results.results.length > 0 && (
          <ResultsTable 
            data={results.results} 
            title="Query Results" 
            downloadable={true}
          />
        )}

        {/* Chart Visualization */}
        {shouldShowChart && (
          <ChartDisplay
            data={chartData}
            type="bar"
            title="Data Visualization"
            description="Graphical representation of your query results"
          />
        )}

        {/* Empty Results */}
        {results.results && results.results.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <Database className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No data found for your query</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 pb-6">
        <h1 className="text-3xl font-bold text-gray-900">Natural Language Query Assistant</h1>
        <p className="mt-2 text-gray-600">
          Ask business questions in plain English. Our AI will translate them to SQL and execute against your data.
        </p>
      </div>

      {/* Team ID Input */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <Users className="h-5 w-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Team Information</h3>
        </div>
        <div className="max-w-md">
          <label htmlFor="queryTeamId" className="block text-sm font-medium text-gray-700 mb-2">
            Team ID (optional)
          </label>
          <input
            type="text"
            id="queryTeamId"
            value={teamId}
            onChange={(e) => setTeamId(e.target.value)}
            placeholder="Enter your team ID for scoring"
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
          />
        </div>
      </div>

      {/* Query Input */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <Search className="h-5 w-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Ask a Question</h3>
        </div>
        
        <div className="space-y-4">
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
              Natural Language Query
            </label>
            <textarea
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="e.g., Show me total spend per vendor this quarter"
              rows={3}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
            <p className="mt-1 text-sm text-gray-500">
              Press Ctrl+Enter (Cmd+Enter on Mac) to execute
            </p>
          </div>
          
          <button
            onClick={executeQuery}
            disabled={!query.trim() || loading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Processing...
              </>
            ) : (
              <>
                <Search className="h-4 w-4 mr-2" />
                Execute Query
              </>
            )}
          </button>
        </div>
      </div>

      {/* Suggestions */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <Lightbulb className="h-5 w-5 text-yellow-600" />
          <h3 className="text-lg font-semibold text-gray-900">Suggested Queries</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {suggestions.slice(0, 6).map((suggestion, index) => (
            <button
              key={index}
              onClick={() => useSuggestion(suggestion)}
              className="text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-sm"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>

      {/* Recent Queries */}
      {history.length > 0 && (
        <div className="card">
          <div className="flex items-center space-x-2 mb-4">
            <Clock className="h-5 w-5 text-gray-600" />
            <h3 className="text-lg font-semibold text-gray-900">Recent Queries</h3>
          </div>
          <div className="space-y-2">
            {history.map((item, index) => (
              <div key={index} className="p-3 bg-gray-50 rounded-lg">
                <div className="flex justify-between items-start">
                  <button
                    onClick={() => useHistoryQuery(item)}
                    className="text-left text-sm text-gray-900 hover:text-primary-600 font-medium"
                  >
                    {item.natural_language_query}
                  </button>
                  <span className="text-xs text-gray-500">
                    {new Date(item.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="mt-1 text-xs text-gray-500">
                  {item.result_count} results • {item.execution_time?.toFixed(3)}s
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Results */}
      {renderResults()}
    </div>
  );
};

export default QueryAssistant;
