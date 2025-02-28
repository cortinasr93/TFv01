// tf-frontend/app/register/publisher/page.tsx

'use client';

import { useState } from 'react';
// import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Check } from 'lucide-react';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';
import ScrollAnimation from '../../components/ScrollAnimation';
import StripeOnboarding from '@/app/components/StripeOnboarding';

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
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
  companyName: string;
  website: string;
  contentType: string;
  contentCategories: string[];
  message: string;
  acceptedTerms: boolean;
}

// interface RegistrationResponse {
//   publisher_id: string;
//   session_id: string;
//   onboarding_url: string;
//   stripe_account_id: string;
// }

export default function PublisherRegistration() {
  // const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});

  const [onboardingData, setOnboardingData] = useState<{
    publisherId: string;
    onboardingUrl: string;
    loginCredentials: {
      email: string;
      password: string;
    };
  } | null>(null);

  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    companyName: '',
    website: '',
    contentType: '',
    contentCategories: [],
    message: '',
    acceptedTerms: false,
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

  const handleCategoryChange = (category: string, checked: boolean) => {
    setFormData(prev => ({
        ...prev,
        contentCategories: checked
        ? [...prev.contentCategories, category]
        : prev.contentCategories.filter(c => c !== category)
    }));
  }

  const validate = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.name) newErrors.name = 'Name is required';
    if (!formData.email) {
        newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
        newErrors.email = 'Please provide valid email address';
    }

    if (!formData.password) {
        newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
        newErrors.password = 'Password must be at least 8 characters';
    }

    if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
    }

    if (!formData.companyName) newErrors.companyName = 'Company name is required';
    if (!formData.website) newErrors.website = 'Website is required';
    if (!formData.contentType) newErrors.contentType = 'Content type is required';

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
        console.log('Sending registration request to:', `${process.env.NEXT_PUBLIC_API_URL}/api/onboarding/publisher`);
        console.log('With data:', formData);

        const response = await fetch('/api/register/publisher', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        const data = await response.json();
        console.log('Registration response:', data);
        
        if (!response.ok) {
            if (data.detail === 'Email already registered') {
                setErrors({ email: 'This email is already registered' });
            } else {
                setErrors({ submit: data.detail || 'Registration failed. Please try again.' });
            }
            return;
        }

        setSubmitted(true);
        console.log('Setting onboarding data...');
        // Store onboarding data to trigger Stripe onboarding
        setOnboardingData({
          publisherId: data.publisher_id,
          onboardingUrl: data.onboarding_url,
          loginCredentials: {
            email: formData.email,
            password: formData.password
          }
        });
        console.log('Onboarding data set');

      } catch (error) {
        console.error('Registration error:', error);
        setErrors({ submit: 'An unexpected error occurred' });
      } finally {
        setLoading(false);
      }
  };

  
    // If we have onboarding data, show the stripe onboarding component
    if (onboardingData) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-[#b1c9a7] via-[#e9efe6] to-[#79a267]">
          <Navbar />
          <div className="py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-2xl mx-auto">
              <StripeOnboarding
                publisherId={onboardingData.publisherId}
                onboardingUrl={onboardingData.onboardingUrl}
                loginCredentials={onboardingData.loginCredentials}
              />
            </div>
          </div>
          <Footer />
        </div>
      );
    }
  
  if (submitted) {
    return(
      <div className="min-h-screen bg-gradient-to-br from-[#b1c9a7] via-[#e9efe6] to-[#79a267]">
          <Navbar />
          <div className="py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md mx-auto">
              <div className="bg-white p-8 shadow-lg rounded-lg text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Check className="w-8 h-8 text-green-600" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Thank You for Joining TrainFair!</h2>
                <p className="text-gray-600 mb-6">
                  We&apos;re excited to help you monetize your content. Our team will reach out with next steps.
                </p>
                <Link 
                  href="/"
                  className="inline-block px-6 py-3 bg-gray-100 rounded-lg text-gray-600 hover:bg-gray-200 transition-colors"
                >
                  Return to Home
                </Link>
              </div>
            </div>
          </div>
          <Footer />
        </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#b1c9a7] via-[#e9efe6] to-[#79a267]">
      <Navbar />

      <div className="py-12 px-4 sm:px-6 lg:px-8">
        <ScrollAnimation>
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-[#1c2617]">Publisher Registration</h2>
            <p className="mt-2 text-[#4a653e]">Join TrainFair and start monetizing your content</p>
          </div>
        </ScrollAnimation>

        <div className="max-w-2xl mx-auto">
          <ScrollAnimation>
            <div className="bg-white py-8 px-4 shadow-lg sm:rounded-lg sm:px-10">
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Account Information */}
                <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
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
                      } shadow-sm focus:border-[#4a653e] focus:ring-[#4a653e]`}
                    />
                    {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
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
                </div>

                {/* Password Fields */}
                <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
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
                </div>

                {/* Company Information */}
                <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
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
                      } shadow-sm focus:border-[#4a653e] focus:ring-[#4a653e]`}
                    />
                    {errors.website && <p className="mt-1 text-sm text-red-600">{errors.website}</p>}
                  </div>
                </div>

                {/* Content Information */}
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
                      } shadow-sm focus:border-[#4a653e] focus:ring-[#4a653e]`}
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

                  {/* Categories */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Content Categories (select all that apply)
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      {['Technology', 'Science', 'Business', 'Health', 'Education', 'Arts', 'Entertainment', 'Finance', 'Sports', 'Culture', 'Other'].map((category) => (
                        <div key={category} className="flex items-center">
                          <input
                            type="checkbox"
                            id={`category-${category}`}
                            checked={formData.contentCategories.includes(category)}
                            onChange={(e) => handleCategoryChange(category, e.target.checked)}
                            className="h-4 w-4 rounded border-gray-300 text-[#4a653e] focus:ring-[#4a653e]"
                          />
                          <label htmlFor={`category-${category}`} className="ml-2 text-sm text-gray-700">
                            {category}
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Message Field */}
                  <div>
                  <label className="block text-sm font-medium text-gray-700" htmlFor="message">
                    Message (Optional)
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    rows={4}
                    value={formData.message}
                    onChange={handleChange}
                    placeholder="Tell us about your content and how you'd like to monetize it..."
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-[#4a653e] focus:ring-[#4a653e]"
                  />
                </div>

                  {/* Terms and Privacy */}
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

                  {/* Error Message */}
                  {errors.submit && (
                    <div className="mt-4 p-2 bg-red-100 text-red-700 rounded">
                      {errors.submit}
                    </div>
                  )}

                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                    <div className="flex">
                      <div className="flex-shrink-0">
                        <svg 
                          className="h-5 w-5 text-blue-400" 
                          viewBox="0 0 20 20" 
                          fill="currentColor"
                        >
                          <path 
                            fillRule="evenodd" 
                            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" 
                            clipRule="evenodd" 
                          />
                        </svg>
                      </div>
                      <div className="ml-3">
                        <p className="text-sm font-medium text-blue-800">After creating your account, you'll be redirected to Stripe to set up your payout information and verify your identity.</p>
                      </div>
                    </div>
                  </div> 

                  {/* Submit Button */}
                  <button
                    type="submit"
                    disabled={loading}
                    className={`w-full flex justify-center items-center gap-2 py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[#4a653e] hover:bg-[#79a267] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#4a653e] transition-colors ${
                      loading ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                  >
                    {loading ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                      </>
                    ) : (
                     <>
                        Create Account & Continue to Stripe
                        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </>
                    )}
                  </button> 

                  <div className="text-center text-sm text-gray-600">
                    Already have an account?{' '}
                    <Link href="/login" className="text-[#4a653e] hover:text-[#79a267] transition-colors">
                      Sign in
                    </Link>
                  </div> 
                </form>
              </div>
            </ScrollAnimation>
          </div>
        </div>
        
      <Footer />
    </div>
  );
}