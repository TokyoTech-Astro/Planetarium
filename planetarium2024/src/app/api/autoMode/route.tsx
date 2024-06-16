import { NextRequest } from "next/server";

export function GET( request: NextRequest ) {
    
}

export function POST( request: NextRequest ) {
    const searchParams = request.nextUrl.searchParams
    const query = searchParams.get('query')
    
}