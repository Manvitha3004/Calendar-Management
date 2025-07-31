import React, { useState } from 'react';

const WorkflowCoordination = ({ onStartWorkflow }) => {
  const [selectedWorkflow, setSelectedWorkflow] = useState('');
  const [workflowParams, setWorkflowParams] = useState({});
  const [isStarting, setIsStarting] = useState(false);

  const workflows = [
    {
      id: 'email_processing',
      name: 'Email Processing',
      description: 'Fetch emails, extract context, generate AI drafts, and create reminders',
      icon: '🟡',
      agents: ['Yellow Agent A', 'Orange Agent A', 'Orange Agent F'],
      parameters: [
        { key: 'max_results', label: 'Max Emails', type: 'number', default: 20 },
        { key: 'priority_filter', label: 'Priority Filter', type: 'select', options: ['all', 'high', 'urgent'], default: 'all' }
      ]
    },
    {
      id: 'schedule_optimization',
      name: 'Schedule Optimization',
      description: 'Analyze calendar, detect conflicts, and optimize scheduling',
      icon: '🟠',
      agents: ['Orange Agent B', 'Orange Agent C', 'Orange Agent E', 'Orange Agent F'],
      parameters: [
        { key: 'days_ahead', label: 'Days Ahead', type: 'number', default: 30 },
        { key: 'optimization_type', label: 'Optimization Type', type: 'select', options: ['daily', 'weekly', 'monthly'], default: 'weekly' }
      ]
    },
    {
      id: 'conflict_resolution',
      name: 'Conflict Resolution',
      description: 'Detect scheduling conflicts and auto-reschedule with buffer time',
      icon: '🔴',
      agents: ['Orange Agent B', 'Orange Agent E', 'Orange Agent F', 'Super Orange Agent'],
      parameters: [
        { key: 'buffer_minutes', label: 'Buffer Time (minutes)', type: 'number', default: 15 },
        { key: 'auto_resolve', label: 'Auto Resolve', type: 'boolean', default: false }
      ]
    },
    {
      id: 'meeting_analysis',
      name: 'Meeting Analysis',
      description: 'Analyze meeting patterns and generate insights',
      icon: '📊',
      agents: ['Orange Agent D', 'Super Orange Agent'],
      parameters: [
        { key: 'analysis_period', label: 'Analysis Period', type: 'select', options: ['week', 'month', 'quarter'], default: 'month' }
      ]
    }
  ];

  const handleWorkflowSelect = (workflowId) => {
    setSelectedWorkflow(workflowId);
    const workflow = workflows.find(w => w.id === workflowId);
    if (workflow) {
      const defaultParams = {};
      workflow.parameters.forEach(param => {
        defaultParams[param.key] = param.default;
      });
      setWorkflowParams(defaultParams);
    }
  };

  const handleParameterChange = (key, value) => {
    setWorkflowParams(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleStartWorkflow = async () => {
    if (!selectedWorkflow) return;
    
    setIsStarting(true);
    try {
      await onStartWorkflow(selectedWorkflow, workflowParams);
      setSelectedWorkflow('');
      setWorkflowParams({});
    } catch (error) {
      console.error('Error starting workflow:', error);
    } finally {
      setIsStarting(false);
    }
  };

  const selectedWorkflowData = workflows.find(w => w.id === selectedWorkflow);

  return (
    <div className="space-y-6">
      {/* Workflow Selection */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Available Workflows</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {workflows.map((workflow) => (
            <div
              key={workflow.id}
              onClick={() => handleWorkflowSelect(workflow.id)}
              className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                selectedWorkflow === workflow.id
                  ? 'border-purple-500 bg-purple-50'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center space-x-3 mb-2">
                <span className="text-2xl">{workflow.icon}</span>
                <h3 className="font-medium text-gray-900">{workflow.name}</h3>
              </div>
              <p className="text-sm text-gray-600 mb-3">{workflow.description}</p>
              <div className="flex flex-wrap gap-1">
                {workflow.agents.map((agent, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                  >
                    {agent}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Workflow Configuration */}
      {selectedWorkflowData && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Configure Workflow</h2>
          
          <div className="mb-6">
            <div className="flex items-center space-x-3 mb-2">
              <span className="text-2xl">{selectedWorkflowData.icon}</span>
              <h3 className="text-lg font-medium text-gray-900">{selectedWorkflowData.name}</h3>
            </div>
            <p className="text-gray-600">{selectedWorkflowData.description}</p>
          </div>

          {/* Parameters */}
          {selectedWorkflowData.parameters.length > 0 && (
            <div className="space-y-4 mb-6">
              <h4 className="font-medium text-gray-900">Parameters</h4>
              {selectedWorkflowData.parameters.map((param) => (
                <div key={param.key} className="flex items-center space-x-4">
                  <label className="w-32 text-sm font-medium text-gray-700">
                    {param.label}:
                  </label>
                  <div className="flex-1">
                    {param.type === 'number' && (
                      <input
                        type="number"
                        value={workflowParams[param.key] || param.default}
                        onChange={(e) => handleParameterChange(param.key, parseInt(e.target.value))}
                        className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    )}
                    {param.type === 'select' && (
                      <select
                        value={workflowParams[param.key] || param.default}
                        onChange={(e) => handleParameterChange(param.key, e.target.value)}
                        className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                      >
                        {param.options.map((option) => (
                          <option key={option} value={option}>
                            {option.charAt(0).toUpperCase() + option.slice(1)}
                          </option>
                        ))}
                      </select>
                    )}
                    {param.type === 'boolean' && (
                      <input
                        type="checkbox"
                        checked={workflowParams[param.key] || param.default}
                        onChange={(e) => handleParameterChange(param.key, e.target.checked)}
                        className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                      />
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Agent Flow */}
          <div className="mb-6">
            <h4 className="font-medium text-gray-900 mb-3">Agent Flow</h4>
            <div className="flex items-center space-x-2 overflow-x-auto">
              {selectedWorkflowData.agents.map((agent, index) => (
                <React.Fragment key={agent}>
                  <div className="flex-shrink-0 bg-blue-100 text-blue-800 px-3 py-2 rounded-lg text-sm font-medium">
                    {agent}
                  </div>
                  {index < selectedWorkflowData.agents.length - 1 && (
                    <div className="flex-shrink-0 text-gray-400">→</div>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between">
            <button
              onClick={() => {
                setSelectedWorkflow('');
                setWorkflowParams({});
              }}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleStartWorkflow}
              disabled={isStarting}
              className="bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white px-6 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
            >
              {isStarting && (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              )}
              <span>{isStarting ? 'Starting...' : 'Start Workflow'}</span>
            </button>
          </div>
        </div>
      )}

      {/* Workflow History */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Workflows</h2>
        <div className="space-y-3">
          {/* This would be populated with actual workflow history */}
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <span className="text-lg">🟡</span>
              <div>
                <div className="font-medium">Email Processing</div>
                <div className="text-sm text-gray-600">Started 5 minutes ago</div>
              </div>
            </div>
            <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full">
              Processing
            </span>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <span className="text-lg">🟠</span>
              <div>
                <div className="font-medium">Schedule Optimization</div>
                <div className="text-sm text-gray-600">Completed 1 hour ago</div>
              </div>
            </div>
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
              Completed
            </span>
          </div>
          
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <span className="text-lg">🔴</span>
              <div>
                <div className="font-medium">Conflict Resolution</div>
                <div className="text-sm text-gray-600">Failed 2 hours ago</div>
              </div>
            </div>
            <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full">
              Failed
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowCoordination;
