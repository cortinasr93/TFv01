// app/api/dashboard/[publisherId]/route.ts
import { NextResponse } from 'next/server'

export async function GET(
  request: Request,
  context: { params : Promise<{ publisherId: string }> }
) {
  const { publisherId } = await context.params;
  
  try {
    const response = await fetch(`http://localhost:8000/api/dashboard/${publisherId}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch dashboard data' }, 
      { status: 500 }
    );
  }
}