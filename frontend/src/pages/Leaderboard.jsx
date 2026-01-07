import React, { useState, useEffect } from 'react';
import { Trophy, Medal, Star, TrendingUp, Users, Activity, Calendar, Plus, Edit, Trash2, Save, X } from 'lucide-react';
import ChartDisplay from '../components/ChartDisplay';
import { API } from '../config/api';


const Leaderboard = () => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [stats, setStats] = useState({});
  const [rankings, setRankings] = useState({});
  const [realtimeActivity, setRealtimeActivity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overall');
  
  // Team management states
  const [showTeamModal, setShowTeamModal] = useState(false);
  const [editingTeam, setEditingTeam] = useState(null);
  const [newTeam, setNewTeam] = useState({ team_id: '', team_name: '' });
  const [teamManagementMode, setTeamManagementMode] = useState(false);

  useEffect(() => {
    fetchLeaderboardData();
    
    // Set up real-time activity polling
    const activityInterval = setInterval(() => {
      fetchRealtimeActivity();
    }, 30000); // Update every 30 seconds
    
    // Set up main data refresh
    const dataInterval = setInterval(() => {
      fetchLeaderboardData();
    }, 60000); // Update every minute
    
    return () => {
      clearInterval(activityInterval);
      clearInterval(dataInterval);
    };
  }, []);

  const fetchLeaderboardData = async () => {
    setLoading(true);
    try {
  const [leaderboardRes, statsRes, rankingsRes] = await Promise.all([
    fetch(`${API.LEADERBOARD}/`),
    fetch(`${API.LEADERBOARD}/stats`),
    fetch(`${API.LEADERBOARD}/rankings`)
  ]);


      const [leaderboardData, statsData, rankingsData] = await Promise.all([
        leaderboardRes.json(),
        statsRes.json(),
        rankingsRes.json()
      ]);

      if (leaderboardData.success) {
        setLeaderboard(leaderboardData.leaderboard);
      }
      
      if (statsData.success) {
        setStats(statsData.stats);
      }
      
      if (rankingsData.success) {
        setRankings(rankingsData.rankings);
      }
    } catch (error) {
      console.error('Error fetching leaderboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRealtimeActivity = async () => {
    try {
      const response = await fetch(`${API.LEADERBOARD}/activity`);
      const data = await response.json();
      
      if (data.success) {
        setRealtimeActivity(data);
        
        // Update the most active team in stats if we have real-time data
        if (data.most_active_team) {
          setStats(prevStats => ({
            ...prevStats,
            most_active_team: {
              team_name: data.most_active_team.team_name,
              activity: data.most_active_team.total_activity,
              activity_status: data.most_active_team.activity_status,
              recent_queries: data.most_active_team.recent_queries,
              last_updated: data.most_active_team.last_updated
            }
          }));
        }
      }
    } catch (error) {
      console.error('Error fetching real-time activity:', error);
    }
  };

  // Team Management Functions
  const createTeam = async (teamData) => {
    try {
      const response = await fetch(`${API.LEADERBOARD}/create-team`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(teamData)
      });
      
      const result = await response.json();
      if (result.success) {
        await fetchLeaderboardData(); // Refresh data
        setShowTeamModal(false);
        setNewTeam({ team_id: '', team_name: '' });
        alert('Team created successfully!');
      } else {
        alert(`Error: ${result.error}`);
      }
    } catch (error) {
      console.error('Error creating team:', error);
      alert('Failed to create team');
    }
  };

  const updateTeamScore = async (teamId, updates) => {
    try {
      const response = await fetch(`${API.LEADERBOARD}/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          team_id: teamId,
          ...updates
        })
      });
      
      const result = await response.json();
      if (result.success) {
        await fetchLeaderboardData(); // Refresh data
        setEditingTeam(null);
        alert('Team updated successfully!');
      } else {
        alert(`Error: ${result.error}`);
      }
    } catch (error) {
      console.error('Error updating team:', error);
      alert('Failed to update team');
    }
  };

  const deleteTeam = async (teamId) => {
    if (!confirm('Are you sure you want to delete this team? This action cannot be undone.')) {
      return;
    }
    
    try {
      // Note: We need to add a delete endpoint to the backend
      const response = await fetch(`${API.LEADERBOARD}/team/${teamId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        await fetchLeaderboardData(); // Refresh data
        alert('Team deleted successfully!');
      } else {
        alert('Failed to delete team');
      }
    } catch (error) {
      console.error('Error deleting team:', error);
      alert('Failed to delete team');
    }
  };

  const getRankIcon = (rank) => {
    switch (rank) {
      case 1:
        return <Trophy className="h-6 w-6 text-yellow-500" />;
      case 2:
        return <Medal className="h-6 w-6 text-gray-400" />;
      case 3:
        return <Medal className="h-6 w-6 text-amber-600" />;
      default:
        return <span className="w-6 h-6 flex items-center justify-center text-sm font-bold text-gray-500">#{rank}</span>;
    }
  };

  const getRankBadge = (rank) => {
    if (rank <= 3) {
      return `bg-gradient-to-r ${
        rank === 1 ? 'from-yellow-400 to-yellow-600' :
        rank === 2 ? 'from-gray-300 to-gray-500' :
        'from-amber-400 to-amber-600'
      } text-white`;
    }
    return 'bg-gray-100 text-gray-800';
  };

  const renderLeaderboardTable = (data, title, scoreKey = 'score') => {
    if (!data || data.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500">
          <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>No teams found</p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <div className="space-y-2">
          {data.slice(0, 10).map((team, index) => (
            <div
              key={team.team_id || index}
              className={`p-4 rounded-lg border-2 transition-all ${
                index < 3 ? getRankBadge(index + 1) + ' border-transparent' : 'bg-white border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  {getRankIcon(team.rank || index + 1)}
                  <div>
                    <h4 className={`font-semibold ${index < 3 ? 'text-white' : 'text-gray-900'}`}>
                      {team.team_name}
                    </h4>
                    <p className={`text-sm ${index < 3 ? 'text-white opacity-90' : 'text-gray-600'}`}>
                      Team ID: {team.team_id}
                    </p>
                  </div>
                </div>
                <div className="text-right flex items-center gap-3">
                  <div>
                    <div className={`text-2xl font-bold ${index < 3 ? 'text-white' : 'text-gray-900'}`}>
                      {team[scoreKey] || 0}
                    </div>
                    <div className={`text-sm ${index < 3 ? 'text-white opacity-90' : 'text-gray-600'}`}>
                      {scoreKey === 'score' ? 'points' : scoreKey.replace('_', ' ')}
                    </div>
                  </div>
                  
                  {/* Team Management Actions */}
                  {teamManagementMode && (
                    <div className="flex gap-2">
                      <button
                        onClick={() => setEditingTeam(team)}
                        className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                        title="Edit Team"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => deleteTeam(team.team_id)}
                        className="p-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                        title="Delete Team"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
              
              {scoreKey === 'score' && (
                <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className={`${index < 3 ? 'text-white opacity-90' : 'text-gray-600'}`}>
                      Validations: {team.validations_completed || 0}
                    </span>
                  </div>
                  <div>
                    <span className={`${index < 3 ? 'text-white opacity-90' : 'text-gray-600'}`}>
                      Queries: {team.queries_executed || 0}
                    </span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderStatsCards = () => {
    const statCards = [
      {
        title: 'Total Teams',
        value: stats.total_teams || 0,
        icon: Users,
        color: 'text-blue-600',
        bgColor: 'bg-blue-50'
      },
      {
        title: 'Total Score',
        value: stats.total_score || 0,
        icon: Star,
        color: 'text-yellow-600',
        bgColor: 'bg-yellow-50'
      },
      {
        title: 'Total Validations',
        value: stats.total_validations || 0,
        icon: Activity,
        color: 'text-green-600',
        bgColor: 'bg-green-50'
      },
      {
        title: 'Total Queries',
        value: stats.total_queries || 0,
        icon: TrendingUp,
        color: 'text-purple-600',
        bgColor: 'bg-purple-50'
      }
    ];

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <div key={index} className={`card ${stat.bgColor}`}>
            <div className="flex items-center">
              <stat.icon className={`h-8 w-8 ${stat.color}`} />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value.toLocaleString()}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderCharts = () => {
    if (!leaderboard || leaderboard.length === 0) return null;

    const topTeamsData = leaderboard.slice(0, 10).map(team => ({
      label: team.team_name,
      value: team.score,
      team_name: team.team_name
    }));

    const activityData = leaderboard.slice(0, 10).map(team => ({
      x: team.validations_completed || 0,
      y: team.score || 0,
      team_name: team.team_name
    }));

    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartDisplay
          data={topTeamsData}
          type="bar"
          title="Top 10 Teams by Score"
          description="Overall performance ranking"
        />
        <ChartDisplay
          data={activityData}
          type="scatter"
          title="Score vs Validations"
          description="Relationship between validations and scores"
        />
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-3 text-gray-600">Loading leaderboard...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 pb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Hackathon Leaderboard</h1>
            <p className="mt-2 text-gray-600">
              Real-time rankings and team performance metrics for the Invoice-PO Matching challenge.
            </p>
          </div>
          
          {/* Team Management Controls */}
          <div className="flex gap-3">
            <button
              onClick={() => setTeamManagementMode(!teamManagementMode)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                teamManagementMode 
                  ? 'bg-red-600 text-white hover:bg-red-700' 
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {teamManagementMode ? (
                <>
                  <X className="h-4 w-4 inline mr-1" />
                  Exit Admin
                </>
              ) : (
                <>
                  <Edit className="h-4 w-4 inline mr-1" />
                  Manage Teams
                </>
              )}
            </button>
            
            <button
              onClick={() => setShowTeamModal(true)}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
            >
              <Plus className="h-4 w-4 inline mr-1" />
              Add Team
            </button>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      {renderStatsCards()}

      {/* Top Performers Highlight */}
      {stats.top_team && (
        <div className="bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold">🏆 Current Leader</h2>
              <p className="text-lg mt-1">{stats.top_team.team_name}</p>
              <p className="text-yellow-100">Score: {stats.top_team.score} points</p>
            </div>
            <Trophy className="h-16 w-16 text-yellow-200" />
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overall', label: 'Overall Ranking', icon: Trophy },
            { id: 'validations', label: 'By Validations', icon: Activity },
            { id: 'queries', label: 'By Queries', icon: TrendingUp },
            { id: 'recent', label: 'Most Active', icon: Calendar }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="h-4 w-4 mr-2" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          {activeTab === 'overall' && renderLeaderboardTable(leaderboard, 'Overall Rankings')}
          {activeTab === 'validations' && renderLeaderboardTable(rankings.by_validations, 'Top Teams by Validations', 'validations_completed')}
          {activeTab === 'queries' && renderLeaderboardTable(rankings.by_queries, 'Top Teams by Queries', 'queries_executed')}
          {activeTab === 'recent' && renderLeaderboardTable(rankings.most_recent, 'Most Recently Active', 'score')}
        </div>
        
        <div className="space-y-6">
          {/* Quick Stats */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Average Score</span>
                <span className="font-medium">{stats.average_score || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Active Teams (24h)</span>
                <span className="font-medium">{stats.recent_activity || 0}</span>
              </div>
              {realtimeActivity && realtimeActivity.recent_activity && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Teams Active Now</span>
                  <span className="font-medium text-green-600">
                    {realtimeActivity.recent_activity.length}
                  </span>
                </div>
              )}
              {stats.most_active_team && (
                <div className="pt-3 border-t border-gray-200">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-sm text-gray-600">Most Active Team</p>
                    {stats.most_active_team.activity_status && (
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        stats.most_active_team.activity_status === 'Very Active' ? 'bg-green-100 text-green-800' :
                        stats.most_active_team.activity_status === 'Active' ? 'bg-blue-100 text-blue-800' :
                        stats.most_active_team.activity_status === 'Recently Active' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {stats.most_active_team.activity_status}
                      </span>
                    )}
                  </div>
                  <p className="font-medium">{stats.most_active_team.team_name}</p>
                  <div className="text-sm text-gray-500 space-y-1">
                    <p>{stats.most_active_team.activity} total activities</p>
                    {stats.most_active_team.recent_queries !== undefined && (
                      <p className="text-green-600">
                        {stats.most_active_team.recent_queries} queries today
                      </p>
                    )}
                    {stats.most_active_team.last_updated && (
                      <p className="text-xs">
                        Last active: {new Date(stats.most_active_team.last_updated).toLocaleTimeString()}
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Real-time Activity Updates */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              <div className="flex items-center justify-between">
                <span>Recent Activity</span>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-xs text-gray-500">Live</span>
                </div>
              </div>
            </h3>
            <div className="space-y-2 text-sm">
              {realtimeActivity && realtimeActivity.activity_timestamp && (
                <p className="text-xs text-gray-500 mb-3">
                  Last updated: {new Date(realtimeActivity.activity_timestamp).toLocaleTimeString()}
                </p>
              )}
              <p className="text-gray-600">
                🔄 Updates every 30 seconds
              </p>
              <p className="text-gray-600">
                📊 Points: Validations (+20/+10), Queries (+10)
              </p>
              <p className="text-gray-600">
                🏆 Rankings based on total score
              </p>
              {realtimeActivity && realtimeActivity.recent_activity && realtimeActivity.recent_activity.length > 0 && (
                <div className="pt-2 border-t border-gray-200">
                  <p className="text-sm font-medium text-gray-700 mb-2">Teams Active Today:</p>
                  <div className="space-y-1">
                    {realtimeActivity.recent_activity.slice(0, 3).map((team, idx) => (
                      <div key={team.team_id} className="flex justify-between text-xs">
                        <span className="text-gray-600">{team.team_name}</span>
                        <span className="text-blue-600">
                          {team.queries_last_1h > 0 ? `${team.queries_last_1h} queries (1h)` : 
                           team.queries_last_24h > 0 ? `${team.queries_last_24h} queries (24h)` : 
                           'Recently active'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Recent Updates */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">System Info</h3>
            <div className="space-y-2 text-sm">
              <p className="text-gray-600">
                🔄 Auto-refresh every 60 seconds
              </p>
              <p className="text-gray-600">
                📊 Real-time activity tracking
              </p>
              <p className="text-gray-600">
                🏆 Rankings based on total score
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      {renderCharts()}
      
      {/* Team Creation Modal */}
      {showTeamModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Create New Team</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Team ID
                </label>
                <input
                  type="text"
                  value={newTeam.team_id}
                  onChange={(e) => setNewTeam({...newTeam, team_id: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., team-001"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Team Name
                </label>
                <input
                  type="text"
                  value={newTeam.team_name}
                  onChange={(e) => setNewTeam({...newTeam, team_name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., Code Warriors"
                />
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => createTeam(newTeam)}
                disabled={!newTeam.team_id || !newTeam.team_name}
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                <Save className="h-4 w-4 inline mr-1" />
                Create Team
              </button>
              <button
                onClick={() => {
                  setShowTeamModal(false);
                  setNewTeam({ team_id: '', team_name: '' });
                }}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
              >
                <X className="h-4 w-4 inline mr-1" />
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Team Edit Modal */}
      {editingTeam && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Update Team Scores</h3>
            <p className="text-gray-600 mb-4">Team: {editingTeam.team_name}</p>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Score Adjustment
                </label>
                <input
                  type="number"
                  id="scoreIncrement"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter points to add/subtract"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Validation Count Adjustment
                </label>
                <input
                  type="number"
                  id="validationIncrement"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter validation count to add"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Query Count Adjustment
                </label>
                <input
                  type="number"
                  id="queryIncrement"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter query count to add"
                />
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => {
                  const scoreIncrement = parseInt(document.getElementById('scoreIncrement').value) || 0;
                  const validationIncrement = parseInt(document.getElementById('validationIncrement').value) || 0;
                  const queryIncrement = parseInt(document.getElementById('queryIncrement').value) || 0;
                  
                  updateTeamScore(editingTeam.team_id, {
                    score_increment: scoreIncrement,
                    validation_increment: validationIncrement,
                    query_increment: queryIncrement
                  });
                }}
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
              >
                <Save className="h-4 w-4 inline mr-1" />
                Update
              </button>
              <button
                onClick={() => setEditingTeam(null)}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
              >
                <X className="h-4 w-4 inline mr-1" />
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Leaderboard;
