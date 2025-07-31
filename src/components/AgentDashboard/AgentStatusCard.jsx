import React from 'react';

const AgentStatusCard = ({ agent }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'processing':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'idle':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'stopped':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const getAgentIcon = (agentType) => {
    switch (agentType) {
      case 'yellow':
        return '🟡';
      case 'orange':
        return '🟠';
      case 'super_orange':
        return '🔴';
      default:
        return '🤖';
    }
  };

  const formatLastActivity = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">{getAgentIcon(agent.agent_type)}</span>
          <div>
            <h3 className="font-medium text-gray-900">{agent.agent_name}</h3>
            <p className="text-sm text-gray-500">{agent.agent_id}</p>
          </div>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(agent.status)}`}>
          {agent.status}
        </span>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Processed:</span>
          <span className="font-medium">{agent.processed_items || 0}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Errors:</span>
          <span className="font-medium text-red-600">{agent.error_count || 0}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Last Activity:</span>
          <span className="font-medium">{formatLastActivity(agent.last_activity)}</span>
        </div>
      </div>

      {agent.current_task && (
        <div className="mt-3 p-2 bg-blue-50 rounded border-l-4 border-blue-400">
          <p className="text-sm font-medium text-blue-800">Current Task:</p>
          <p className="text-sm text-blue-600">{agent.current_task}</p>
        </div>
      )}

      {agent.performance_metrics && Object.keys(agent.performance_metrics).length > 0 && (
        <div className="mt-3">
          <p className="text-sm font-medium text-gray-700 mb-1">Performance:</p>
          <div className="space-y-1">
            {Object.entries(agent.performance_metrics).map(([key, value]) => (
              <div key={key} className="flex justify-between text-xs">
                <span className="text-gray-600">{key}:</span>
                <span className="font-medium">{value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentStatusCard;
