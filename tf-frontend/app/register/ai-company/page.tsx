// tf-frontend/app/register/ai-company/page.tsx

'use client';

import { useState } from 'react';
// import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Check } from 'lucide-react';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';
import ScrollAnimation from '../../components/ScrollAnimation';

interface FormErrors {
  name?: string;
  companyName?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  useCase?: string;
  website?: string;
  submit?: string;
}

interface FormData {
  name: string;
  companyName: string;
  email: string;
  password: string;
  confirmPassword: string;
  website: string;
  // billingEmail: string;
  useCases: string[];
  message: string;
  acceptedTerms: boolean;
}

export default function AICompanyRegistration() {
  // const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});

  const [formData, setFormData] = useState<FormData>({
    name: '',
    companyName: '',
    email: '',
    password: '',
    confirmPassword: '',
    website: '',
    useCases: [],
    message: '',
    //billingEmail: '',
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

  const handleUseCaseChange = (useCase: string, checked: boolean) => {
    setFormData(prev => ({
      ...prev,
      useCases: checked
        ? [...prev.useCases, useCase]
        : prev.useCases.filter(c => c !== useCase)
    }));
  };
  
  const validate = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.name) newErrors.name = 'Name is required';
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

    if (formData.useCases.length === 0) {
      newErrors.useCase = 'Please select at least one use case';
    }
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

      const data = await response.json();

      if (!response.ok) {
        if (data.detail === 'Email already registered') {
          setErrors({ email: 'This email is already registered' });
        } else {
          setErrors({ submit: data.detail || 'Registration failed. Please try again.' });
        }
        return;
      }

      setSubmitted(true);
    } catch (error) {
      console.error('Registration error:', error);
      setErrors({ submit: 'An unexpected error occurred' });
    } finally {
      setLoading(false);
    }

    //   // After successful registration, redirect to company dashboard
    //   router.push(`/dashboard/ai-company/${data.company_id}`);
    // } catch (error) {
    //   setErrors({ submit: 'Registration failed. Please try again.' });
    // } finally {
    //   setLoading(false);
    // }
  };

  if (submitted) {
    return (
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
                We&apos;re excited to help you access high-quality training data. Our team will reach out with next steps.
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
            <h2 className="text-3xl font-bold text-[#1c2617]">AI Company Registration</h2>
            <p className="mt-2 text-[#4a653e]">Join TrainFair and access high-quality training data</p>
          </div>
        </ScrollAnimation>

        <div className="max-w-2xl mx-auto">
          <ScrollAnimation>
            <div className="bg-white py-8 px-4 shadow-lg sm:rounded-lg sm:px-10">
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Basic Information */}
                <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700" htmlFor="name">
                      Full Name *
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      required
                      className={`mt-1 block w-full rounded-md ${
                        errors.name ? 'border-red-500' : 'border-gray-300'
                      } shadow-sm focus:border-[#4a653e] focus:ring-[#4a653e]`}
                    />
                    {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name}</p>}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700" htmlFor="email">
                      Email Address *
                    </label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      className={`mt-1 block w-full rounded-md ${
                        errors.email ? 'border-red-500' : 'border-gray-300'
                      } shadow-sm focus:border-[#4a653e] focus:ring-[#4a653e]`}
                    />
                    {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email}</p>}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700" htmlFor="companyName">
                    Company Name *
                  </label>
                  <input
                    type="text"
                    id="companyName"
                    name="companyName"
                    value={formData.companyName}
                    onChange={handleChange}
                    required
                    className={`mt-1 block w-full rounded-md ${
                      errors.companyName ? 'border-red-500' : 'border-gray-300'
                    } shadow-sm focus:border-[#4a653e] focus:ring-[#4a653e]`}
                  />
                  {errors.companyName && <p className="mt-1 text-sm text-red-600">{errors.companyName}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700" htmlFor="website">
                    Website URL *
                  </label>
                  <input
                    type="url"
                    id="website"
                    name="website"
                    value={formData.website}
                    onChange={handleChange}
                    placeholder="https://"
                    required
                    className={`mt-1 block w-full rounded-md ${
                      errors.website ? 'border-red-500' : 'border-gray-300'
                    } shadow-sm focus:border-[#4a653e] focus:ring-[#4a653e]`}
                  />
                  {errors.website && <p className="mt-1 text-sm text-red-600">{errors.website}</p>}
                </div>

                {/* Use Cases */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Intended Use Cases (select all that apply) *
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[
                      { id: 'training', label: 'Model Training' },
                      { id: 'rag', label: 'Retrieval-Augmented Generation (RAG)' },
                      { id: 'search', label: 'AI-Enhanced Search' },
                      { id: 'other', label: 'Other Use Cases' }
                    ].map((useCase) => (
                      <div key={useCase.id} className="flex items-center">
                        <input
                          type="checkbox"
                          id={`useCase-${useCase.id}`}
                          checked={formData.useCases.includes(useCase.id)}
                          onChange={(e) => handleUseCaseChange(useCase.id, e.target.checked)}
                          className="h-4 w-4 rounded border-gray-300 text-[#4a653e] focus:ring-[#4a653e]"
                        />
                        <label htmlFor={`useCase-${useCase.id}`} className="ml-2 text-sm text-gray-700">
                          {useCase.label}
                        </label>
                      </div>
                    ))}
                  </div>
                  {errors.useCase && <p className="mt-1 text-sm text-red-600">{errors.useCase}</p>}
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
                    placeholder="Tell us about your AI company and your data needs..."
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-[#4a653e] focus:ring-[#4a653e]"
                  />
                </div>

                {/* Terms and Conditions */}
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
                  <div className="p-4 bg-red-50 text-red-700 rounded-lg">
                    {errors.submit}
                  </div>
                )}

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className={`w-full flex justify-center items-center py-3 px-4 rounded-lg text-white bg-[#4a653e] hover:bg-[#79a267] transition-colors ${
                    loading ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </>
                  ) : (
                    'Submit'
                  )}
                </button>

                {/* <p className="text-center text-sm text-gray-500">
                  Already have an account?{' '}
                  <Link href="/login" className="text-[#4a653e] hover:text-[#79a267] transition-colors">
                    Sign in
                  </Link>
                </p> */}
              </form>
            </div>
          </ScrollAnimation>
        </div>
      </div>
      
      <Footer />
    </div>
  );
}