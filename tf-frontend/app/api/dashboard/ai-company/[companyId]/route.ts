// tf-frontend/app/api/dashboard/ai-company/[companyId]/route.ts

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { API_URL } from '@/config/api';

type RouteParams = {
    params: { 
        companyId: string 
    };
};

export async function GET(
    _request: NextRequest, 
    { params }: { params: { companyId: string } }
) {
    try {
        // Get session cookie
        const cookieStore = await cookies();
        const sessionId = cookieStore.get('session_id');

        if (!sessionId) {
            return NextResponse.json({ error: 'No session found' }, { status: 401 });
        }
        
        // Forward request to backend with session cookie
        const response = await fetch(
            `${API_URL}/api/dashboard/ai-company/${params.companyId}`, 
            {
                headers: {
                    'Cookie': `session_id=${sessionId}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        if (!response.ok) {
            const error = await response.json();
            return NextResponse.json(error, { status: response.status });
        }

        const data = await response.json();
        return NextResponse.json(data);
        
    } catch (error) {
        console.error('Error fetching AI company dashboard data:', error);
        return NextResponse.json(
            { error: 'Failed to fetch dashboard data' },
            { status: 500 }
        );
    }
}
