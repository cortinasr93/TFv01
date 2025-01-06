'use client';

import { useState, useEffect } from 'react';
import { use } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, PieChart, 
  Pie, Cell 
} from 'recharts';
import { Users, Bot, Activity } from 'lucide-react';

interface Detection {
  time: string;
  ipAddress: string;
  botType: string;
  confidence: number;
  detectionMethod: string;
}

interface DashboardData {
  publisherName: string;
  stats: {
    totalRequests: number;
    botPercentage: number;
    uniqueIPs: number;
  };
  timeSeriesData: Array<{
    time: string;
    total: number;
    bots: number;
  }>;
  botTypes: Array<{
    name: string;
    value: number;
  }>;
  earnings?: {
    totalEarned: number;
    currentBalance: number;
    lastPayout?: string;
  };
  recentDetections: Detection[]
}

interface ErrorProps {
    message: string;
}

function Loading() {
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-lg">Loading dashboard...</div>
    </div>
  );
}

function ErrorMessage({ message }: ErrorProps) {
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-lg text-red-600">{message}</div>
    </div>
  );
}

export default function PublisherDashboard({ params }: { params: Promise<{ publisherId: string }> }) {
  const resolvedParams = use(params);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<DashboardData | null>(null);
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        console.log('Starting dashboard data fetch');

        const response = await fetch(`/api/dashboard/publisher/${resolvedParams.publisherId}`, {
          credentials: 'include'
        });
        console.log('Response received:', response.status);

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Error data:', errorData);
            throw new Error(errorData.details || 'Failed to fetch dashboard data');
        }

        const dashboardData = await response.json();
        console.log('Data successfully fetched');
        setData(dashboardData);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [resolvedParams.publisherId]);

  if (loading) return <Loading />;
  if (error) return <ErrorMessage message={error as string} />;
  if (!data) return <ErrorMessage message="No data available" />;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">{data.publisherName} Analytics</h1>
        <p className="mt-2 text-gray-600">Monitor your content usage and earnings</p>
      </div>

      {/* Stats and Earnings Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
        {/* Stats Column */}
        <div className="lg:col-span-2 grid grid-cols-1 gap-4">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="mr-4">
                <Users className="h-8 w-8 text-blue-500" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">Total Requests</h3>
                <p className="text-2xl">{data.stats.totalRequests.toLocaleString()}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="mr-4">
                <Bot className="h-8 w-8 text-yellow-500" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">Bot Percentage</h3>
                <p className="text-2xl">{data.stats.botPercentage}%</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <div className="mr-4">
                <Activity className="h-8 w-8 text-gray-500" />
              </div>
              <div>
                <h3 className="text-lg font-semibold">Unique IPs</h3>
                <p className="text-2xl">{data.stats.uniqueIPs.toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Earnings Card */}
        <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow">
          <div className="flex flex-col h-full justify-center">
            <h3 className="text-lg font-semibold mb-2">Total Earnings</h3>
            <p className="text-4xl font-bold text-green-600">
              ${data.earnings?.totalEarned.toLocaleString(undefined, {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
              }) || '0.00'}
            </p>
            <div className="mt-4 text-sm text-gray-600">
              <div className="flex justify-between mb-1">
                <span>Current Balance</span>
                <span className="font-medium">
                  ${data.earnings?.currentBalance.toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  }) || '0.00'}
                </span>
              </div>
              {data.earnings?.lastPayout && (
                <div className="flex justify-between">
                  <span>Last Payout</span>
                  <span className="font-medium">
                    {new Date(data.earnings.lastPayout).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Traffic Over Time</h3>
          <div className="h-[300px]">
            <ResponsiveContainer>
              <LineChart data={data.timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="total" 
                  stroke="#8884d8" 
                  name="Total Traffic" 
                />
                <Line 
                  type="monotone" 
                  dataKey="bots" 
                  stroke="#82ca9d" 
                  name="Bot Traffic" 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Bot Types Distribution</h3>
          <div className="h-[300px]">
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={data.botTypes}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {data.botTypes.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={COLORS[index % COLORS.length]} 
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}