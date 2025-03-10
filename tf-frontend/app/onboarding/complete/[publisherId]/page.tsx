// tf-frontend/app/onboarding/complete/[publisherId]/page.tsx

'use client'

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { fetchApi } from '@/utils/api';

interface PageProps {
    params: Promise<{ publisherId: string }>
}

export default function OnboardingComplete(props: PageProps) {

    const router = useRouter();
    const [error, setError] = useState<string | null>(null);
    const [status, setStatus] = useState<'verifying' | 'completed' | 'error'>('verifying');
    const [publisherId, setPublisherId] = useState<string | null>(null);

    useEffect(() => {
      const initParams = async () => {
        try {
          const { publisherId } = await props.params;
          setPublisherId(publisherId);
        } catch (err) {
          console.error('Error getting params:', err);
          setError('Invalid publisher ID');
          setStatus('error');
        }
      };
      initParams();
    }, [props.params]);
    
    useEffect(() => {
        if (!publisherId) return;
        
        const completeOnboarding = async () => {
            try {
                console.log('Starting onboarding completion for publisher:', publisherId);

                // Verify onboarding completion
                const response = await fetchApi(`/onboarding/publisher/${publisherId}/complete`, {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    cache: 'no-store'
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    console.error('Completion error:', errorData);
                    throw new Error(errorData.detail || 'Failed to verify onboarding completion');
                }
                
                const data = await response.json();
                console.log('Completion response:', data);

                if (!data.onboarding_complete) {
                    throw new Error('Onboarding was not completed successfully');
                }

                setStatus('completed');

                // After successful completion, try to perform automatic login
              
                const loginResponse = await fetchApi('/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: data.email,
                        password: data.password,
                        userType: 'publisher'
                    }),
                    credentials: 'include',
                    cache: 'no-store' 
                });

                if (loginResponse.ok) {
                    setTimeout(() => {
                        router.push(`/dashboard/publisher/${publisherId}`);
                    }, 2000);
                } else{
                    throw new Error('Login failed after onboarding');
                }
                
            } catch (err) {
                console.error('Onboarding completion error:', err);
                setError(err instanceof Error ? err.message : 'An unexpected error occurred');
                setStatus('error');

                // Redirect to login after error
                setTimeout(() => {
                    router.push('/login');
                }, 3000);
            }
        };

        completeOnboarding();
    }, [publisherId, router]);

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
          <div className="sm:mx-auto sm:w-full sm:max-w-md">
            <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
              <div className="text-center">
                {error ? (
                  <>
                    <div className="rounded-full bg-red-100 p-3 mx-auto w-fit">
                      <svg 
                          className="h-6 w-6 text-red-600" 
                          fill="none" 
                          viewBox="0 0 24 24" 
                          stroke="currentColor"
                      >
                          <path 
                              strokeLinecap="round" 
                              strokeLinejoin="round" 
                              strokeWidth={2} 
                              d="M6 18L18 6M6 6l12 12" 
                          />
                      </svg>
                    </div>
                    <h2 className="mt-4 text-lg font-medium text-gray-900">Onboarding Error</h2>
                    <p className="mt-2 text-sm text-gray-500">{error}</p>
                    <p className="mt-2 text-sm text-gray-500">Redirecting to login...</p>
                  </>
              ) : status === 'verifying' ? (
                  <>
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
                    <h2 className="mt-4 text-lg font-medium text-gray-900">Verifying Setup</h2>
                    <p className="mt-2 text-sm text-gray-500">Please wait while we verify your account setup...</p>
                  </>
                ) : (
                  <>
                    <div className="rounded-full bg-green-100 p-3 mx-auto w-fit">
                      <svg 
                        className="h-6 w-6 text-green-600" 
                        fill="none" 
                        viewBox="0 0 24 24" 
                        stroke="currentColor"
                      >
                        <path 
                          strokeLinecap="round" 
                          strokeLinejoin="round" 
                          strokeWidth={2} 
                          d="M5 13l4 4L19 7" 
                        />
                      </svg>
                    </div>
                    <h2 className="mt-4 text-lg font-medium text-gray-900">Setup Complete!</h2>
                    <p className="mt-2 text-sm text-gray-500">Redirecting to your dashboard...</p>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
    );

}