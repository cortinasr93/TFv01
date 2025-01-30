// lib/config.ts

interface Environment {
    apiUrl: string;
    stripePublishableKey: string;
    environment: 'development' | 'production';

}

const development: Environment = {
    apiUrl: 'http://localhost:8000',
    stripePublishableKey: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || '',
    environment: 'development'
};

const production: Environment = {
    apiUrl: process.env.NEXT_PUBLIC_API_URL || 'https://trainfair.io/api',
    stripePublishableKey: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || '',
    environment: 'production'
};

export const config: Environment = process.env.NODE_ENV === 'production' ? production : development;

// API route helpers
export const getApiRoute = (path: string): string => {
    return `${config.apiUrl}${path.startsWith('/') ? path : `/${path}`}`;
};

// Fetch wrapper with credentials and error handling
export async function fetchApi<T>(
    path: string,
    options: RequestInit = {}
): Promise<T> {
    const url = getApiRoute(path);

    const defaultOptions: RequestInit = {
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
    };

    const response = await fetch(url, {
        ...defaultOptions,
        ...options,
    });

    if (!response.ok) {
        let errorMessage: string;
        try {
            const errorData = await response.json();
            errorMessage = errorData.detail || 'An error occurred';
        } catch {
            errorMessage = 'An error occurred';
        }
        throw new Error(errorMessage);
    }

    return response.json();
}