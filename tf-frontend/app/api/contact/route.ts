// tf-frontend/app/api/contact/route.ts

import { NextResponse } from 'next/server';
import { fetchApi } from '@/utils/api';
import { ApiError } from '@/utils/api';

export async function POST(request: Request) {
    try {
        const data = await request.json();

        // Forward request to backend
        const response = await fetchApi('/api/contact', {
            method: 'POST',
            body: JSON.stringify(data)
        });

        const result = await response.json();
        return NextResponse.json(result);

    } catch (error) {
        console.error('Error in contact API route:', error);
        return NextResponse.json(
            { error: error instanceof ApiError ? error.message : 'Failed to send message' },
            { status: error instanceof ApiError ? error.status : 500 }
        );
    }
}