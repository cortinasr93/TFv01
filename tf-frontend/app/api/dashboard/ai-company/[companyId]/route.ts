// tf-frontend/app/api/dashboard/ai-company/[companyId]/route.ts

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { fetchApi } from '@/utils/api';

type Params = Promise<{ companyId: string }>

export async function GET(
    request: NextRequest, 
    props: { params: Params }
): Promise<NextResponse> {
    try {

        const params = await props.params;
        
        // Get session cookie
        const cookieStore = await cookies();
        const sessionId = cookieStore.get('session_id');

        if (!sessionId) {
            return NextResponse.json({ error: 'No session found' }, { status: 401 });
        }
        
        // Forward request to backend with session cookie
        const response = await fetchApi(`/dashboard/ai-company/${params.companyId}`, {
            method: 'GET',
            headers: {
                'Cookie': `session_id=${sessionId.value}`,
                'Content-Type': 'application/json'
            },
            cache: 'no-store'
        });

        if (!response.ok) {
            const errorData = await response.json();
            
            // Handle specific error cases
            if (response.status === 403) {
                return NextResponse.json(
                    { error: 'Not authorized to view this dashboard' },
                    { status: 403 }
                );
            }

            throw new Error(errorData.detail || 'Failed to fetch dashboard data');
        }

        const data = await response.json();
        return NextResponse.json(data);
        
    } catch (error) {
        console.error('AI Company Dashboard error:', error);
        
        // Enhanced error handling
        const statusCode = error instanceof Response ? error.status : 500;
        const errorMessage = error instanceof Error 
            ? error.message 
            : 'An error occurred while fetching dashboard data';

        return NextResponse.json(
            { error: errorMessage },
            { status: statusCode }
        );
    }
}
