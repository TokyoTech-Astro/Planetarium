import { type NextRequest } from "next/server"
const { spawn } = require('node:child_process')

let child: any

const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': '*',
    'Access-Control-Allow-Headers': '*'
}

export async function  POST(request: NextRequest) {
    const searchParams = request.nextUrl.searchParams
    const query = searchParams.get('query')
    if(query == 'start'){
        if(child !== undefined && child.exitCode === null){
            console.log('Auto mode is already running.')
            return new Response("Auto mode is already running.", {headers: corsHeaders})
        }
        console.log('Run auto mode.')
        child = spawn('./src/app/api/autoMode/autoMode.py',{ stdio: 'inherit'})
        return new Response("Auto mode started.", {headers: corsHeaders})
    }

    else if(query == 'stop'){
        if(child !== undefined && child.exitCode === null) {
            child.kill()
            console.log('stop auto mode')
            return new Response("stop", {headers: corsHeaders})
        }
        else {
            console.log('Auto mode is not started yet/')
            return new Response("Auto mode is not started yet", {headers: corsHeaders})
        }
    }
}

export async function OPTIONS() {
    return new Response("", {headers: corsHeaders})
}
