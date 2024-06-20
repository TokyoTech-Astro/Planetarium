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

export async function  POST() {
    for(let i of k2023){
        if("star" in i){
            if(i["star"] !== undefined){
                for(let pin of i["star"]){
                    if(pin > 0){
                        try {
                            const res = await axios.put(`http://pi-starsphere.local:8000/led/${pin}?state=True`)
                            console.log(`${yellow}■${reset} Turn on ${pin}.`)
                        }
                        catch (e) { console.log(e) }
                    }
                    else if(pin <0){
                        try {
                            const res = await axios.put(`http://pi-starsphere.local:8000/led/${-pin}?state=False`)
                            console.log(`${yellow}■${reset} Turn off ${pin}.`)
                        }
                        catch (e) { console.log(e) }
                    }
                }
            }
        }

        if("motor" in i){
            try {
                if(i["motor"] !== undefined){
                    if(i["motor"] >= 0) {
                        const res = await axios.post(`http://pi-controller.local:8000/motor?dir=forward&deg=${i["motor"]}&speed=medium`)
                        console.log(`${green}■${reset} Start rotation. (dir:forward, deg:${i["motor"]}, speed:medium)`)
                    }
                    else if(i["motor"] < 0) {
                        const res = await axios.post(`http://pi-controller.local:8000/motor?dir=back&deg=${-i["motor"]}&speed=medium`)
                        console.log(`${green}■${reset} Start rotation. (dir:back, deg:${i["motor"]}, speed:medium)`)
                    }

                }
            }
            catch (e) { console.log(e) } 
        }

        if("audio" in i){
            try {
                if(i["audio"] !== undefined){
                    const res = await axios.post(`http://pi-controller.local:8001/audio?filename=${i["audio"]}`)
                    console.log(`${blue}■${reset} Playing ${i["audio"]}.`)
                }
            }
            catch (e) { console.log(e) }
        }

        if("interval" in i){
            const sleep = (sec: number) => new Promise((res) => setTimeout(res, sec*1000));
            if(i["interval"] == "end"){
                for(let led of leds){
                    try {
                        const res = await axios.put(`http://pi-starsphere.local:8000/led/${led.pin}?state=False`)
                        console.log(`${magenta}■${reset} Turn off ${led.pin}.`)
                    }
                    catch (e) { console.log(e) }
                }
            }
            else if(typeof(i["interval"]) == "number"){
                console.log(`${magenta}■${reset} Interval of ${i["interval"]} sec.`)
                await sleep(i["interval"])
            }
        }

        console.log("")
    }

    return new Response("")
}