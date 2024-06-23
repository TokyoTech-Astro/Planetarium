import axios from 'axios'
import k2023 from '@/k2023.json'
import leds from '@/leds.json'

const black   = '\u001b[30m';
const red     = '\u001b[31m';
const green   = '\u001b[32m';
const yellow  = '\u001b[33m';
const blue    = '\u001b[34m';
const magenta = '\u001b[35m';
const cyan    = '\u001b[36m';
const white   = '\u001b[37m';
const reset   = '\u001b[0m';

const putLed = async (pin: number, state: boolean) => {
    try {
        const res = await axios.put(`http://pi-starsphere.local:8000/led/${pin}?state=${state}`)
        console.log(`${yellow}■${reset} Set LED state. (pin:${pin}, state:${state}).`)
    }
    catch (e) { console.error(e) }
}

const handleLed = (pins: number[] | undefined) => {
    if(pins !== undefined){
        for(let pin of pins){
            if(pin>0) putLed(pin, true)
            else putLed(-pin, false)
        }
    }
}

const postMotor = async (dir:string, deg:number, speed:string) => {
    try {
        const res = await axios.post(`http://pi-controller.local:8000/motor?dir=${dir}&deg=${deg}&speed=${speed}`)
        console.log(`${green}■${reset} Start rotation. (dir:${dir}, deg:${deg}, speed:${speed})`)
    }
    catch (e) { console.error(e) }
}

const handleMotor = (deg: number | undefined) => {
    if(deg !== undefined){
        if(deg > 0) postMotor("forward", deg, "medium")
        else postMotor("back", -deg, "medium")
    }
}

const postAudio = async (filename: string | undefined) => {
    try {
        if(filename !== undefined){
            const res = await axios.post(`http://pi-controller.local:8001/audio?filename=${filename}`)
            console.log(`${blue}■${reset} Playing ${filename}.`)
        }
    }
    catch (e) { console.error(e) }
}

const handleInterval = async (interval: string | number | undefined) => {
    const sleep = (sec: number) => new Promise((res) => setTimeout(res, sec*1000));
    if(interval == "end") for(let led of leds) putLed(led.pin, false)
    else if(typeof interval == "number"){
        console.log(`${magenta}■${reset} Interval of ${interval} sec.`)
        await sleep(interval)
    }
}

export default async function  autoMode() {
    for(let i of k2023){
        if('star' in i) handleLed(i['star'])
        if("motor" in i) handleMotor(i["motor"])
        if("audio" in i) postAudio(i["audio"]) 
        if("interval" in i) await handleInterval(i["interval"])
        console.log("")
    }
}