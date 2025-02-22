// tf-frontend/app/api/dashboard/publisher/[publisherId]/route.ts

import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { fetchApi } from '@/utils/api';

type Params = Promise<{ publisherId: string }>

export async function GET(
  request: NextRequest, 
  props: { params : Params }
): Promise<NextResponse> {
  try {
    
    const params = await props.params;
    
    // Get session cookie
    const cookieStore = await cookies();
    const sessionId = cookieStore.get('session_id');

    console.log('Fetching dashboard with session:', sessionId?.value);

    if (!sessionId) {
      return NextResponse.json({ error: 'No session found' }, { status: 401 });
    }

    const response = await fetchApi(`/dashboard/publisher/${params.publisherId}`, {
        credentials: 'include',
        headers: {
            'Cookie': `session_id=${sessionId.value}`, // Forward cookies from the request
            'Content-Type': 'application/json'
        },
        cache: 'no-store' // Ensure we get fresh data
    });

    console.log('Dashboard response status:', response.status);
    const text = await response.text();
    console.log('Dashboard response text:', text);

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

    const data = await response.json;
    return NextResponse.json(data);

  } catch (error) {
    console.error('Error fetching dashboard data:', error);

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