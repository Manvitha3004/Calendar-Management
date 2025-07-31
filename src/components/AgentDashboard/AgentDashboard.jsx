import React, { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import AgentStatusCard from './AgentStatusCard';
import AgentTaskList from './AgentTaskList';
import AgentMetrics from './AgentMetrics';
import WorkflowCoordination from './WorkflowCoordination';

const AgentDashboard = () => {
  const { token } = useAuth();
  const [agents, setAgents] = useState({ yellow: [], orange: [], super_orange: [] });
  const [tasks, setTasks] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchAgentData();
    const interval = setInterval(fetchAgentData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchAgentData = async () => {
    try {
      // Fetch agent status
      const agentResponse = await fetch('/api/agents/status');
      const agentData = await agentResponse.json();
      if (agentData.status === 'success') {
        setAgents(agentData.agents);
      }

      // Fetch recent tasks
      const taskResponse = await fetch('/api/agents/tasks?limit=20');
      const taskData = await taskResponse.json();
      if (taskData.status === 'success') {
        setTasks(taskData.tasks);
      }

      // Fetch metrics
      const metricsResponse = await fetch('/api/agents/metrics');
      const metricsData = await metricsResponse.json();
      if (metricsData.status === 'success') {
        setMetrics(metricsData);
      }

      setLoading(false);
    } catch (error) {
      console.error('Error fetching agent data:', error);
      setLoading(false);
    }
  };

  const startWorkflow = async (workflowType, parameters = {}) => {
    try {
      const response = await fetch('/api/agents/coordinate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_type: workflowType,
          user_id: 'current_user', // In production, get from auth
          parameters: {
            ...parameters,
            user_token: token
          }
        }),
      });

      const data = await response.json();
      if (data.status === 'success') {
        alert(`${workflowType} workflow started successfully!`);
        fetchAgentData(); // Refresh data
      }
    } catch (error) {
      console.error('Error starting workflow:', error);
      alert('Failed to start workflow');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Agent Dashboard</h1>
        <p className="text-gray-600">Monitor and control your AI assistant agents</p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', name: 'Overview' },
            { id: 'agents', name: 'Agents' },
            { id: 'tasks', name: 'Tasks' },
            { id: 'workflows', name: 'Workflows' },
            { id: 'metrics', name: 'Metrics' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-purple-500 text-purple-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* System Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">System Status</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {metrics?.summary?.active_agents || 0}
                </div>
                <div className="text-sm text-green-600">Active Agents</div>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {metrics?.summary?.total_tasks || 0}
                </div>
                <div className="text-sm text-blue-600">Total Tasks</div>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {metrics?.summary?.overall_success_rate || 0}%
                </div>
                <div className="text-sm text-purple-600">Success Rate</div>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {tasks.filter(t => t.status === 'processing').length}
                </div>
                <div className="text-sm text-yellow-600">Processing</div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={() => startWorkflow('email_processing')}
                className="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-3 rounded-lg font-medium transition-colors"
              >
                🟡 Process Emails
              </button>
              <button
                onClick={() => startWorkflow('schedule_optimization')}
                className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-3 rounded-lg font-medium transition-colors"
              >
                🟠 Optimize Schedule
              </button>
              <button
                onClick={() => startWorkflow('conflict_resolution')}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-3 rounded-lg font-medium transition-colors"
              >
                🔴 Resolve Conflicts
              </button>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
            <div className="space-y-3">
              {tasks.slice(0, 5).map((task) => (
                <div key={task.task_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <div className="font-medium">{task.task_type}</div>
                    <div className="text-sm text-gray-600">
                      {task.agent_info?.agent_name} • {new Date(task.created_at).toLocaleTimeString()}
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    task.status === 'completed' ? 'bg-green-100 text-green-800' :
                    task.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                    task.status === 'failed' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {task.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'agents' && (
        <div className="space-y-6">
          {/* Yellow Agents */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4 text-yellow-600">🟡 Yellow Agents</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {agents.yellow.map((agent) => (
                <AgentStatusCard key={agent.agent_id} agent={agent} />
              ))}
            </div>
          </div>

          {/* Orange Agents */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4 text-orange-600">🟠 Orange Agents</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {agents.orange.map((agent) => (
                <AgentStatusCard key={agent.agent_id} agent={agent} />
              ))}
            </div>
          </div>

          {/* Super Orange Agent */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4 text-red-600">🔴 Super Orange Agent</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {agents.super_orange.map((agent) => (
                <AgentStatusCard key={agent.agent_id} agent={agent} />
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'tasks' && (
        <AgentTaskList tasks={tasks} onRefresh={fetchAgentData} />
      )}

      {activeTab === 'workflows' && (
        <WorkflowCoordination onStartWorkflow={startWorkflow} />
      )}

      {activeTab === 'metrics' && metrics && (
        <AgentMetrics metrics={metrics} />
      )}
    </div>
  );
};

export default AgentDashboard;
