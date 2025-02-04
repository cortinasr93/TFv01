// tf-frontend/app/components/StripeOnboarding.tsx

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface StripeOnboardingProps {
    publisherId: string;
    onboardingUrl: string;
    loginCredentials: {
        email: string;
        password: string
    };
}

interface OnboardingError {
    detail: string;
}

const StripeOnboarding: React.FC<StripeOnboardingProps> = ({ publisherId, onboardingUrl, loginCredentials }) => {
    
    const router = useRouter();
    const [error, setError] = useState<string | null>(null);
    const [isRedirecting, setIsRedirecting] = useState(false);
    const [isCompletingSetup, setIsCompletingSetup] = useState(false);

    useEffect(() => {

        // Check if this is a return from Stripe onboarding
        const checkOnboardingStatus = async () => {
            if (window.location.pathname.includes('/onboarding/complete')) {
                setIsCompletingSetup(true);
                try {
                    // Verify onboarding completion
                    const response = await fetch(`/api/onboarding/publisher/${publisherId}/complete`, {
                        method: 'POST',
                        credentials: 'include'
                    });

                    if (!response.ok) {
                        throw new Error('Failed to verify onboarding completion');
                    }
                    // Perform automatic login
                    const loginResponse = await fetch ('api/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            email: loginCredentials.email,
                            password: loginCredentials.password,
                            userType: 'publisher'
                        })
                    });

                    if (!loginResponse.ok) {
                        router.push('/login');
                        return;
                    }

                    // Redirect to dashboard
                    router.push(`/dashboard/publisher/${publisherId}`);
                } catch (err) {
                    setError(err instanceof Error ? err.message : 'An unexpected error occurred');
                    setTimeout(() => {
                        router.push('/login');
                    }, 3000);
                }
            }
        };

        if (onboardingUrl && !isCompletingSetup) {
            setIsRedirecting(true);
            window.location.href = onboardingUrl;
        } else {
            checkOnboardingStatus();
        }
    }, [onboardingUrl, publisherId, loginCredentials, router, isCompletingSetup]);

    const handleRefresh = async () => {
        try {
            setError(null);
            const response = await fetch(`/api/onboarding/publisher/${publisherId}/refresh-link`, {
                method: 'POST',
                credentials: 'include',
            });

            if (!response.ok) {
                const errorData = await response.json() as OnboardingError;
                throw new Error(errorData.detail || 'Failed to refresh onboarding link');
            }

            const data = await response.json() as { onboardingUrl: string };
            // Redirect to new onboarding URL
            window.location.href = data.onboardingUrl;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unexpected error occurred');
        }
    };

    if (error) {
        return (
          <div className="p-4 rounded-md bg-red-50 border border-red-200">
            <p className="text-red-700">{error}</p>
            <button
              onClick={handleRefresh}
              className="mt-2 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              Try Again
            </button>
          </div>
        );
    }
    
    if (isCompletingSetup) {
        return (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
            <p className="text-lg text-gray-600">Completing account setup...</p>
          </div>
        );
    }
    
    if (isRedirecting) {
        return (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
            <p className="text-lg text-gray-600">Redirecting to Stripe onboarding...</p>
          </div>
        );
    }
    
    return (
        <div className="text-center py-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Complete Your Account Setup</h2>
          <p className="text-gray-600 mb-6">
            You&apos;ll be redirected to Stripe to complete your account setup and enable payments.
          </p>
          <button
            onClick={() => window.location.href = onboardingUrl}
            className="px-6 py-3 bg-[#4a653e] text-white rounded-lg hover:bg-[#79a267] transition-colors"
          >
            Continue to Stripe
          </button>
        </div>
    );
};

export default StripeOnboarding