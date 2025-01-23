// tf-frontend/app/api/dashboard/ai-company/[companyId]/route.ts

import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

interface Props {
    params: { companyId: string }
};

export async function GET(request: Request, { params }: Props) {
    try {
        // Get session cookie
        const cookieStore = await cookies();
        const sessionId = cookieStore.get('session_id');

        if (!sessionId) {
            return NextResponse.json({ error: 'No session found' }, { status: 401 });
        }
        
        // Forward request to backend with session cookie
        const response = await fetch(`http://localhost:8000/api/dashboard/ai-company/${params.companyId}`, {
            headers: {
                'Cookie': `session_id=${sessionId.value}`,
                'Content-Type': 'application/json'
            }
        });

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
