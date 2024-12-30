// app/api/dashboard/route.ts
import { NextResponse } from 'next/server';
import { API_BASE_URL } from '@/lib/config';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function GET() {
  try {
    //TODO: In production, get publisherId from session/auth
    const publisherId = 'test-123'; // Temporary test ID
    const url = `${API_URL}/api/dashboard/${publisherId}`;
    
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Accept': 'application/json'
        }
    });
    console.log('Response status:', response.status)
    
    if (!response.ok) {
        const errorText = await response.text();
        console.error('Backend error response:', errorText);
        throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Successfully received data from backend');
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Detailed API route error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch dashboard data' },
      { status: 500 }
    );
  }
}