import { NextRequest } from "next/server";

export function GET(
    request: NextRequest,
    { params }: { params: {pin: number}}
) {
    const pin = params.pin
    
}

export function PUT(
    request: NextRequest,
    { params }: { params: {pin: number}}
) {
    const pin = params.pin

    const searchParams = request.nextUrl.searchParams
    const onoff = searchParams.get('onoff')

    
}