'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import ScrollAnimation from '../components/ScrollAnimation';

interface FormData {
  email: string;
  password: string;
  userType: 'publisher' | 'ai-company';
}

export default function Login() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
    userType: 'publisher'
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');  // Clear error when user makes changes
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        credentials: 'include',
        headers: { 
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });
      
      // If we get redirect, let browser handle it
      if (response.redirected) {
        window.location.href = response.url;
        return;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || data.detail || 'Login failed');
      }

    } catch (err) {
        console.error('Login error:', err)
        setError(err instanceof Error ? err.message : 'Login failed. Please try again');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#b1c9a7] via-[#e9efe6] to-[#79a267]">
      <Navbar />
      
      <div className="flex flex-col justify-center pt-32 pb-12 sm:px-6 lg:px-8">
        <ScrollAnimation>
          <div className="sm:mx-auto sm:w-full sm:max-w-md">
            <h2 className="text-center text-3xl font-bold text-[#1c2617]">
              Sign in to your account
            </h2>
            <p className="mt-2 text-center text-sm text-[#4a653e]">
              Or{' '}
              <Link href="/register" className="font-medium text-[#4a653e] hover:text-[#79a267]">
                register for a new account
              </Link>
            </p>
          </div>
        </ScrollAnimation>

        <ScrollAnimation className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow-lg sm:rounded-lg sm:px-10">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* User Type Selection */}
              <div>
                <label htmlFor="userType" className="block text-sm font-medium text-gray-700">
                  Account Type
                </label>
                <select
                  id="userType"
                  name="userType"
                  value={formData.userType}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-[#4a653e] focus:ring-[#4a653e]"
                >
                  <option value="publisher">Publisher</option>
                  <option value="ai-company">AI Company</option>
                </select>
              </div>

              {/* Email Field */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email address
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-[#4a653e] focus:ring-[#4a653e]"
                />
              </div>

              {/* Password Field */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-[#4a653e] focus:ring-[#4a653e]"
                />
              </div>

              {/* Error Message */}
              {error && (
                <div className="text-red-600 text-sm">
                  {error}
                </div>
              )}

              {/* Submit Button */}
              <div>
                <button
                  type="submit"
                  disabled={loading}
                  className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[#4a653e] hover:bg-[#79a267] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#4a653e] transition-colors ${
                    loading ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  {loading ? 'Signing in...' : 'Sign in'}
                </button>
              </div>
            </form>
          </div>
        </ScrollAnimation>
      </div>
      
      <Footer />
    </div>
  );
}