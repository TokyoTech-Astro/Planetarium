import autoMode from './autoMode';

export async function  POST() {
    autoMode()
    return new Response("auto-mode start")
}