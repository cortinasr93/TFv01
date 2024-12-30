'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

interface FormErrors {
  name?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  companyName?: string;
  website?: string;
  contentType?: string;
  submit?: string;
}

interface FormData {
  // Step 1: Account Information
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
  
  // Step 2: Publisher Details
  companyName: string;
  website: string;
  contentType: string;
  description: string;
  
  // Step 3: Content Details
  contentCategories: string[];
  estimatedVolume: string;
  updateFrequency: string;
  
  // Step 4: Terms
  acceptedTerms: boolean;
  acceptedPrivacy: boolean;
}

export default function PublisherRegistration() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});

  const [formData, setFormData] = useState<FormData>({
    // Step 1
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    
    // Step 2
    companyName: '',
    website: '',
    contentType: '',
    description: '',
    
    // Step 3
    contentCategories: [],
    estimatedVolume: '',
    updateFrequency: '',
    
    // Step 4
    acceptedTerms: false,
    acceptedPrivacy: false,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const checked = (e.target as HTMLInputElement).checked;

    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));

    // Clear error when field is modified
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const validateStep = (stepNumber: number): boolean => {
    const newErrors: FormErrors = {};

    if (stepNumber === 1) {
      if (!formData.name) newErrors.name = 'Name is required';
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
    }

    if (stepNumber === 2) {
      if (!formData.companyName) newErrors.companyName = 'Company name is required';
      if (!formData.website) newErrors.website = 'Website is required';
      if (!formData.contentType) newErrors.contentType = 'Content type is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateStep(step)) return;

    if (step < 4) {
      setStep(step + 1);
      return;
    }

    setLoading(true);
    
    try {
      const response = await fetch('/api/register/publisher', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Registration failed');
      }

      const data = await response.json();
      router.push('/dashboard');
      
    } catch (error) {
      setErrors({ submit: 'Registration failed. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (step) {
      case 1:
        return (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">1. Account Information</h2>

            {/* Name Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="name">
                Full Name
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className={`mt-1 block w-full rounded-md ${
                  errors.name ? 'border-red-500' : 'border-gray-300'
                } shadow-sm focus:border-indigo-500 focus:ring-indigo-500`}
              />
              {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
            </div>

            {/* Email Field */}
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
                } shadow-sm focus:border-indigo-500 focus:ring-indigo-500`}
              />
              {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
            </div>

            {/* Password Fields */}
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
                } shadow-sm focus:border-indigo-500 focus:ring-indigo-500`}
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
                } shadow-sm focus:border-indigo-500 focus:ring-indigo-500`}
              />
              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>
              )}
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">2. Publisher Details</h2>

            {/* Company Name */}
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
                } shadow-sm focus:border-indigo-500 focus:ring-indigo-500`}
              />
              {errors.companyName && (
                <p className="mt-1 text-sm text-red-600">{errors.companyName}</p>
              )}
            </div>

            {/* Website */}
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="website">
                Website URL
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
                } shadow-sm focus:border-indigo-500 focus:ring-indigo-500`}
              />
              {errors.website && <p className="mt-1 text-sm text-red-600">{errors.website}</p>}
            </div>

            {/* Content Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="contentType">
                Content Type
              </label>
              <select
                id="contentType"
                name="contentType"
                value={formData.contentType}
                onChange={handleChange}
                className={`mt-1 block w-full rounded-md ${
                  errors.contentType ? 'border-red-500' : 'border-gray-300'
                } shadow-sm focus:border-indigo-500 focus:ring-indigo-500`}
              >
                <option value="">Select content type</option>
                <option value="news">News Articles</option>
                <option value="blog">Blog Posts</option>
                <option value="academic">Academic Papers</option>
                <option value="documentation">Technical Documentation</option>
                <option value="other">Other</option>
              </select>
              {errors.contentType && (
                <p className="mt-1 text-sm text-red-600">{errors.contentType}</p>
              )}
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="description">
                Description
              </label>
              <textarea
                id="description"
                name="description"
                rows={4}
                value={formData.description}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                placeholder="Tell us about your content..."
              />
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">3. Content Details</h2>

            {/* Content Categories */}
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Content Categories
              </label>
              <div className="mt-2 space-y-2">
                {['Technology', 'Science', 'Business', 'Health', 'Education', 'Arts', 'Entertainment'].map((category) => (
                  <div key={category} className="flex items-center">
                    <input
                      type="checkbox"
                      id={`category-${category}`}
                      name="contentCategories"
                      value={category}
                      checked={formData.contentCategories.includes(category)}
                      onChange={(e) => {
                        const checked = e.target.checked;
                        setFormData(prev => ({
                          ...prev,
                          contentCategories: checked
                            ? [...prev.contentCategories, category]
                            : prev.contentCategories.filter(c => c !== category)
                        }));
                      }}
                      className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                    />
                    <label
                      htmlFor={`category-${category}`}
                      className="ml-2 block text-sm text-gray-700"
                    >
                      {category}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {/* Estimated Volume */}
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="estimatedVolume">
                Estimated Monthly Content Volume
              </label>
              <select
                id="estimatedVolume"
                name="estimatedVolume"
                value={formData.estimatedVolume}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="">Select volume</option>
                <option value="small">Less than 100 pieces</option>
                <option value="medium">100-1000 pieces</option>
                <option value="large">More than 1000 pieces</option>
              </select>
            </div>

            {/* Update Frequency */}
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="updateFrequency">
                Content Update Frequency
              </label>
              <select
                id="updateFrequency"
                name="updateFrequency"
                value={formData.updateFrequency}
                onChange={handleChange}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="">Select frequency</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
              </select>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">4. Terms & Conditions</h2>

            <div className="bg-gray-50 p-4 rounded-md">
              <p className="text-sm text-gray-700">
                By registering, you agree to participate in our content marketplace and allow AI companies
                to use your content for training purposes under the specified terms and conditions.
              </p>
            </div>

            <div className="space-y-4">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="acceptedTerms"
                  name="acceptedTerms"
                  checked={formData.acceptedTerms}
                  onChange={handleChange}
                  className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="acceptedTerms" className="ml-2 text-sm text-gray-700">
                  I accept the <a href="#" className="text-indigo-600 hover:text-indigo-500">Terms and Conditions</a>
                </label>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="acceptedPrivacy"
                  name="acceptedPrivacy"
                  checked={formData.acceptedPrivacy}
                  onChange={handleChange}
                  className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="acceptedPrivacy" className="ml-2 text-sm text-gray-700">
                  I accept the <a href="#" className="text-indigo-600 hover:text-indigo-500">Privacy Policy</a>
                </label>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {[1, 2, 3, 4].map((stepNumber) => (
              <div key={stepNumber} className="flex items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    step >= stepNumber
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {stepNumber}
                </div>
                {stepNumber < 4 && (
                  <div
                    className={`h-0.5 w-16 ${
                      step > stepNumber ? 'bg-indigo-600' : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Form */}
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <form onSubmit={handleSubmit}>
            {renderStepContent()}

            {/* Error Message */}
            {errors.submit && (
              <div className="mt-4 p-2 bg-red-100 text-red-700 rounded">
                {errors.submit}
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="mt-6 flex justify-between">
              {step > 1 && (
                <button
                  type="button"
                  onClick={() => setStep(step - 1)}
                  className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Back
                </button>
              )}
              <button
                type="submit"
                disabled={loading}
                className={`ml-auto flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
                  loading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {loading
                  ? 'Processing...'
                  : step === 4
                  ? 'Complete Registration'
                  : 'Continue'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}