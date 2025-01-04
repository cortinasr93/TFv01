// app/api/dashboard/[publisherId]/route.ts
import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function GET(
  request: Request,
  { params }: { params : { publisherId: string }}
) {  
  try {
    
    const { publisherId } = await params;
    const cookieStore = await cookies();
    const sessionId = cookieStore.get('session_id');

    console.log('Fetching dashboard with session:', sessionId?.value)

    const response = await fetch(`http://localhost:8000/api/dashboard/${publisherId}`, {
        credentials: 'include',
        headers: {
            'Cookie': sessionId ? `session_id=${sessionId.value}` : '', // Forward cookies from the request
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