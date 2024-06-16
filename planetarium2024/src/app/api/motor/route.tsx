import { NextRequest } from "next/server";

export function GET( request: NextRequest ) {
    
}

export function POST( request: NextRequest ) {
    const searchParams = request.nextUrl.searchParams
    const dir = searchParams.get('dir')
    const deg = searchParams.get('deg')
    
}