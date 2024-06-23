import { type NextRequest } from "next/server"
const { execFile } = require('node:child_process')

let child: any

export async function  POST(request: NextRequest) {
    const searchParams = request.nextUrl.searchParams
    const query = searchParams.get('query')
    if(query == 'start'){
        if(child !== undefined && child.exitCode === null){
            return new Response("Auto mode is already running.")
        }
        child = execFile('./src/app/api/autoMode/autoMode.py')
        return new Response("Auto mode started.")
    }

    else if(query == 'stop'){
        if(child !== undefined && child.exitCode === null) {
            child.kill()
            return new Response("stop")
        }
        else return new Response("Auto mode is not started yet")
    }
}