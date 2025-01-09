'use client';

import { useState, useEffect } from 'react';
import { use } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { BarChart2, Database, Receipt, CreditCard } from 'lucide-react';

interface DashboardData {
  companyName: string;
  usageStats: {
    totalTokens: number;
    totalCost: number;
    publishersAccessed: number;
    averageCostPerToken: number;
  };
  timeSeriesData: Array<{
    time: string;
    tokens: number;
    cost: number;
  }>;
  dataSources: Array<{
    publisherId: string;
    publisherName: string;
    tokensUsed: number;
    cost: number;
    publisherEarned: number;
    lastAccessed: string;
    contentType: string;
  }>;
  recentTransactions: Array<{
    id: string;
    date: string;
    amount: number;
    description: string;
    status: string;
  }>;
}

// API response interface to match backend structure
interface APIResponse {
    companyName: string;
    usage_stats: {
      totalTokens: number;
      totalCost: number;
      publishersAccessed: number;
      averageCostPerToken: number;
    };
    timeSeriesData: Array<{
      time: string;
      tokens: number;
      cost: number;
    }>;
    dataSources: Array<{
      publisherId: string;
      publisherName: string;
      tokensUsed: number;
      cost: number;
      publisherEarned: number;
      lastAccessed: string;
      contentType: string;
    }>;
    recentTransactions: Array<{
      id: string;
      date: string;
      amount: number;
      description: string;
      status: string;
    }>;
}

function InitialLoading() {
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-lg">Loading dashboard...</div>
    </div>
  );
}

export default function AICompanyDashboard({ params }: { params: Promise<{ companyId: string }> }) {
  const resolvedParams = use(params);
  const [initialLoad, setInitialLoad] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<DashboardData>({
    companyName: '',
    usageStats: {
        totalTokens: 0,
        totalCost: 0,
        publishersAccessed: 0,
        averageCostPerToken: 0
    },
    timeSeriesData: [],
    dataSources: [],
    recentTransactions: []
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`/api/dashboard/ai-company/${resolvedParams.companyId}`, {
          credentials: 'include'
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch dashboard data');
        }

        const rawData: APIResponse = await response.json();
        console.log("Raw API response:", rawData);

        // Transform data to match our interface
        const transformedData: DashboardData = {
            companyName: rawData.companyName || '',
            usageStats: rawData.usage_stats || {
              totalTokens: 0,
              totalCost: 0,
              publishersAccessed: 0,
              averageCostPerToken: 0
            },
            timeSeriesData: rawData.timeSeriesData || [],
            dataSources: rawData.dataSources || [],
            recentTransactions: rawData.recentTransactions || []
          };

        console.log("Transformed data:", transformedData);
        setData(transformedData);
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
      } finally {
        setInitialLoad(false);
      }
    };
    
    // Initial fetch
    fetchData();

    const intervalId = setInterval(fetchData, 30000);

    return () => clearInterval(intervalId);
}, [resolvedParams.companyId]);

if (initialLoad) return <InitialLoading />;

return (
<div className="p-6 max-w-7xl mx-auto">
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800">{error}</p>
        </div>
      )}

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">{data.companyName} Dashboard</h1>
        <p className="mt-2 text-gray-600">Monitor your API usage and costs</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="mr-4">
              <BarChart2 className="h-8 w-8 text-blue-500" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Total Tokens</h3>
              <p className="text-2xl">{data.usageStats.totalTokens.toLocaleString()}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="mr-4">
              <Receipt className="h-8 w-8 text-green-500" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Total Cost</h3>
              <p className="text-2xl">${data.usageStats.totalCost.toLocaleString(undefined, {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
              })}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="mr-4">
              <Database className="h-8 w-8 text-purple-500" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Publishers</h3>
              <p className="text-2xl">{data.usageStats.publishersAccessed}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="mr-4">
              <CreditCard className="h-8 w-8 text-gray-500" />
            </div>
            <div>
              <h3 className="text-lg font-semibold">Cost/Token</h3>
              <p className="text-2xl">${data.usageStats.averageCostPerToken.toFixed(4)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Usage Over Time</h3>
          <div className="h-[300px]">
            <ResponsiveContainer>
              <LineChart data={data.timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="tokens" 
                  stroke="#8884d8" 
                  name="Tokens Used" 
                />
                <Line 
                  yAxisId="right"
                  type="monotone" 
                  dataKey="cost" 
                  stroke="#82ca9d" 
                  name="Cost ($)" 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Data Sources Table */}
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <h3 className="text-lg font-semibold mb-4">Data Sources</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2">Publisher</th>
                <th className="text-left p-2">Content Type</th>
                <th className="text-left p-2">Tokens Used</th>
                <th className="text-left p-2">Cost</th>
                <th className="text-left p-2">Last Used</th>
              </tr>
            </thead>
            <tbody>
              {data.dataSources.map((source) => (
                <tr key={source.publisherId} className="border-b">
                  <td className="p-2">{source.publisherName}</td>
                  <td className="p-2">{source.contentType}</td>
                  <td className="p-2">{source.tokensUsed.toLocaleString()}</td>
                  <td className="p-2">${source.cost.toFixed(2)}</td>
                  <td className="p-2">{new Date(source.lastAccessed).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Recent Transactions</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2">Date</th>
                <th className="text-left p-2">Description</th>
                <th className="text-left p-2">Amount</th>
                <th className="text-left p-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {data.recentTransactions.map((transaction) => (
                <tr key={transaction.id} className="border-b">
                  <td className="p-2">{new Date(transaction.date).toLocaleDateString()}</td>
                  <td className="p-2">{transaction.description}</td>
                  <td className="p-2">${transaction.amount.toFixed(2)}</td>
                  <td className="p-2">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      transaction.status === 'completed' 
                        ? 'bg-green-100 text-green-800'
                        : transaction.status === 'pending'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {transaction.status.charAt(0).toUpperCase() + transaction.status.slice(1)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
);
}
