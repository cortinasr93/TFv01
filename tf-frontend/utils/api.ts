const API_URL = process.env.NEXT_PUBLIC_API_URL;

export class ApiError extends Error {
    constructor(public status: number, message: string) {
        super(message);
        this.name = 'ApiError';
    }
}

export async function fetchApi(
    endpoint: string,
    options: RequestInit = {}
): Promise<Response> {
    const url = `${API_URL}${endpoint}`;

    const defaultHeaders = {
        'Content-Type': 'application/json',
    };

    try {

        const response = await fetch(url, {
            ...options,
            credentials: 'include',
            headers: {
                ...defaultHeaders,
                ...options.headers, 
            },
        });

        if (!response.ok) {
            let errorMessage;
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || 'An error occurred';
            } catch {
                errorMessage = 'An error occurred';
            }
            throw new ApiError(response.status, errorMessage);
        }

        return response;
    } catch (error) {
        if (error instanceof ApiError) {
            throw error;
        }
        throw new ApiError(500, 'Network error occurred');
    }
}