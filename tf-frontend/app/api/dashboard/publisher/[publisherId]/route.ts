// tf-frontend/app/api/dashboard/publisher/[publisherId]/route.ts

import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

type Props = {
  params: { publisherId: string }
};

export async function GET(request: Request, { params }: Props) {
  try {
    
    // Get session cookie
    const cookieStore = await cookies();
    const sessionId = cookieStore.get('session_id');

    console.log('Fetching dashboard with session:', sessionId?.value);

    if (!sessionId) {
      return NextResponse.json({ error: 'No session found' }, { status: 401 });
    }

    const response = await fetch(`http://localhost:8000/api/dashboard/publisher/${params.publisherId}`, {
        credentials: 'include',
        headers: {
            'Cookie': `session_id=${sessionId.value}`, // Forward cookies from the request
            'Content-Type': 'application/json'
        }
    });

    console.log('Dashboard response status:', response.status);
    const text = await response.text();
    console.log('Dashboard response text:', text);

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    } 

    const data = JSON.parse(text);
    return NextResponse.json(data);

  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch dashboard data' }, 
      { status: 500 }
    );
  }
}