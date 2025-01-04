'use client';

import { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, PieChart, 
  Pie, Cell 
} from 'recharts';
import { Users, Bot, AlertTriangle, Activity } from 'lucide-react';

interface Detection {
  time: string;
  ipAddress: string;
  botType: string;
  confidence: number;
  detectionMethod: string;
}

interface BotType {
  name: string;
  value: number;
}

interface TimeSeriesData {
  time: string;
  total: number;
  bots: number;
}

interface DashboardData {
  timeSeriesData: TimeSeriesData[];
  botTypes: BotType[];
  stats: {
    totalRequests: number;
    botPercentage: number;
    activeThreats: number;
    uniqueIPs: number;
  };
  recentDetections: Detection[];
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

import { use } from 'react';

export default function Dashboard({ params }: { params: Promise<{ publisherId: string }> }) {
  const resolvedParams = use(params);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<DashboardData>({
    timeSeriesData: [],
    botTypes: [],
    stats: {
      totalRequests: 0,
      botPercentage: 0,
      activeThreats: 0,
      uniqueIPs: 0
    },
    recentDetections: []
  });

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        console.log('Starting dashboard data fetch');

        const response = await fetch(`/api/dashboard/${resolvedParams.publisherId}`, {
          credentials: 'include'
        });
        console.log('Response received:', response.status);

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Error data:', errorData);
            throw new Error(errorData.details || errorData.error || `HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('Data successfully fetched');
        setData(result as DashboardData);
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        if (err instanceof Error) {
            setError(err.message);
        } else {
            setError('Failed to load dashboard data. Please try again later.');
        }
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
      <h1 className="text-3xl font-bold mb-6">Bot Detection Dashboard</h1>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="mr-4">
              <Users className="h-8 w-8 text-blue-500" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Total Requests</h3>
              <p className="text-2xl">{data.stats.totalRequests}</p>
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
              <AlertTriangle className="h-8 w-8 text-red-500" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Active Threats</h3>
              <p className="text-2xl">{data.stats.activeThreats}</p>
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
              <p className="text-2xl">{data.stats.uniqueIPs}</p>
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

      {/* Recent Detections Table */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Recent Bot Detections</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2">Time</th>
                <th className="text-left p-2">IP Address</th>
                <th className="text-left p-2">Bot Type</th>
                <th className="text-left p-2">Confidence</th>
                <th className="text-left p-2">Detection Method</th>
              </tr>
            </thead>
            <tbody>
              {data.recentDetections.map((detection, index) => (
                <tr key={index} className="border-b">
                  <td className="p-2">{detection.time}</td>
                  <td className="p-2">{detection.ipAddress}</td>
                  <td className="p-2">{detection.botType}</td>
                  <td className="p-2">{detection.confidence}%</td>
                  <td className="p-2">{detection.detectionMethod}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}