// tf-frontend/app/onboarding/refresh/[publisherId]/page.tsx

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function OnboardingRefresh({ params }: { params: { publisherId: string } }) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const refreshLink = async () => {
      try {
        const response = await fetch(`/api/onboarding/publisher/${params.publisherId}/refresh-link`, {
          method: 'POST',
          credentials: 'include'
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || 'Failed to refresh onboarding link');
        }

        const data = await response.json();
        
        // Redirect to the new onboarding URL
        window.location.href = data.onboardingUrl;

      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unexpected error occurred');
        setIsLoading(false);
        
        // Redirect to login after error
        setTimeout(() => {
          router.push('/login');
        }, 3000);
      }
    };

    refreshLink();
  }, [params.publisherId, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
              <h2 className="mt-4 text-lg font-medium text-gray-900">Refreshing Setup Link</h2>
              <p className="mt-2 text-sm text-gray-500">Please wait while we generate a new setup link...</p>
            </div>
          </div>
        </div>
      </div>
    );
  
  }
  
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
            <div className="text-center">
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
              <h2 className="mt-4 text-lg font-medium text-gray-900">Refresh Error</h2>
              <p className="mt-2 text-sm text-gray-500">{error}</p>
              <p className="mt-2 text-sm text-gray-500">Redirecting to login...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}