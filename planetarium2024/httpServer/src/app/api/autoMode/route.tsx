import axios from 'axios'
import k2023 from '@/k2023.json'

export async function  POST() {
    for(let i of k2023){
        if("star" in i){
            if(i["star"] !== undefined){
                for(let pin of i["star"]){
                    if(pin > 0){
                        try {
                            const res = await axios.put(`http://pi-starsphere.local:8000/led/${pin}?state=True`)
                            console.log(`Turn on ${pin}.`)
                        }
                        catch (e) { console.log(e) }
                    }
                    else if(pin <0){
                        try {
                            const res = await axios.put(`http://pi-starsphere.local:8000/led/${-pin}?state=False`)
                            console.log(`Turn off ${pin}.`)
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
                        console.log(`Start rotation. (dir:forward, deg:${i["motor"]}, speed:medium)`)
                    }
                    else if(i["motor"] < 0) {
                        const res = await axios.post(`http://pi-controller.local:8000/motor?dir=back&deg=${-i["motor"]}&speed=medium`)
                        console.log(`Start rotation. (dir:back, deg:${i["motor"]}, speed:medium)`)
                    }

                }
            }
            catch (e) { console.log(e) } 
        }

        if("audio" in i){
            try {
                if(i["audio"] !== undefined){
                    const res = await axios.post(`http://pi-controller.local:8001/audio?filename=${i["audio"]}`)
                    console.log(`Playing ${i["audio"]}.`)
                }
            }
            catch (e) { console.log(e) }
        }

        if("interval" in i){
            const sleep = (sec: number) => new Promise((res) => setTimeout(res, sec*1000));
            //　　　　　　　　　　　　　　　　　　　　↓後で実装
            if(typeof(i["interval"]) == "string"){ }
            else if(i["interval"] !== undefined){
                await sleep(i["interval"])
                console.log(`Interval of ${i["interval"]} sec.`)
            }
        }
    }

    return new Response("")
}