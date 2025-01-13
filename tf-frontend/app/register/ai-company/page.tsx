'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';
import ScrollAnimation from '../../components/ScrollAnimation';

interface FormErrors {
  companyName?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  website?: string;
  submit?: string;
}

interface FormData {
  companyName: string;
  email: string;
  password: string;
  confirmPassword: string;
  website: string;
  billingEmail: string;
  acceptedTerms: boolean;
}

export default function AICompanyRegistration() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});

  const [formData, setFormData] = useState<FormData>({
    companyName: '',
    email: '',
    password: '',
    confirmPassword: '',
    website: '',
    billingEmail: '',
    acceptedTerms: false,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    
    const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : false;

    setFormData(prev => ({
        ...prev,
        [name]: type === 'checkbox' ? checked : value
    }));

    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const validate = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.companyName) newErrors.companyName = 'Company name is required';
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please provide a valid email address';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    if (!formData.website) newErrors.website = 'Website is required';

    if (!formData.acceptedTerms) {
      newErrors.submit = 'You must accept the Terms and Privacy Policy to register';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      const response = await fetch('/api/register/ai-company', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error('Registration failed');

      const data = await response.json();

      // After successful registration, redirect to company dashboard
      router.push(`/dashboard/ai-company/${data.company_id}`);
    } catch (error) {
      setErrors({ submit: 'Registration failed. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#b1c9a7] via-[#e9efe6] to-[#79a267]">
      <Navbar />

      <div className="py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl mx-auto">
          <ScrollAnimation>
            <div className="bg-white py-8 px-4 shadow-lg sm:rounded-lg sm:px-10">
              <form onSubmit={handleSubmit} className="space-y-6">
                <h2 className="text-2xl font-bold text-[#1c2617] mb-6">AI Company Registration</h2>

                <div>
                  <label className="block text-sm font-medium text-gray-700" htmlFor="companyName">
                    Company Name
                  </label>
                  <input
                    type="text"
                    id="companyName"
                    name="companyName"
                    value={formData.companyName}
                    onChange={handleChange}
                    className={`mt-1 block w-full rounded-md ${
                      errors.companyName ? 'border-red-500' : 'border-gray-300'
                    } shadow-sm focus:border-[#4a653e] focus:ring-[#4a653e]`}
                  />
                  {errors.companyName && (
                    <p className="mt-1 text-sm text-red-600">{errors.companyName}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700" htmlFor="email">
                    Email Address
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className={`mt-1 block w-full rounded-md ${
                      errors.email ? 'border-red-500' : 'border-gray-300'
                    } shadow-sm focus:border-[#4a653e] focus:ring-[#4a653e]`}
                  />
                  {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700" htmlFor="website">
                    Company Website
                  </label>
                  <input
                    type="url"
                    id="website"
                    name="website"
                    value={formData.website}
                    onChange={handleChange}
                    placeholder="https://"
                    className={`mt-1 block w-full rounded-md ${
                      errors.website ? 'border-red-500' : 'border-gray-300'
                    } shadow-sm focus:border-[#4a653e] focus:ring-[#4a653e]`}
                  />
                  {errors.website && <p className="mt-1 text-sm text-red-600">{errors.website}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700" htmlFor="password">
                    Password
                  </label>
                  <input
                    type="password"
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    className={`mt-1 block w-full rounded-md ${
                      errors.password ? 'border-red-500' : 'border-gray-300'
                    } shadow-sm focus:border-[#4a653e] focus:ring-[#4a653e]`}
                  />
                  {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700" htmlFor="confirmPassword">
                    Confirm Password
                  </label>
                  <input
                    type="password"
                    id="confirmPassword"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className={`mt-1 block w-full rounded-md ${
                      errors.confirmPassword ? 'border-red-500' : 'border-gray-300'
                    } shadow-sm focus:border-[#4a653e] focus:ring-[#4a653e]`}
                  />
                  {errors.confirmPassword && (
                    <p className="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700" htmlFor="billingEmail">
                    Billing Email (Optional)
                  </label>
                  <input
                    type="email"
                    id="billingEmail"
                    name="billingEmail"
                    value={formData.billingEmail}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-[#4a653e] focus:ring-[#4a653e]"
                    placeholder="Same as primary email if left empty"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="acceptedTerms"
                    name="acceptedTerms"
                    checked={formData.acceptedTerms}
                    onChange={handleChange}
                    className="h-4 w-4 rounded border-gray-300 text-[#4a653e] focus:ring-[#4a653e]"
                  />
                  <label htmlFor="acceptedTerms" className="ml-2 text-sm text-gray-700">
                    I accept the{' '}
                    <Link href="/terms" className="text-[#4a653e] hover:text-[#79a267] transition-colors">
                      Terms and Conditions
                    </Link>{' '}
                    and{' '}
                    <Link href="/privacy" className="text-[#4a653e] hover:text-[#79a267] transition-colors">
                      Privacy Policy
                    </Link>
                  </label>
                </div>

                {errors.submit && (
                  <div className="mt-4 p-2 bg-red-100 text-red-700 rounded">
                    {errors.submit}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[#4a653e] hover:bg-[#79a267] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#4a653e] transition-colors ${
                    loading ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  {loading ? 'Processing...' : 'Complete Registration'}
                </button>
              </form>
            </div>
          </ScrollAnimation>
        </div>
      </div>
      
      <Footer />
    </div>
  );
}