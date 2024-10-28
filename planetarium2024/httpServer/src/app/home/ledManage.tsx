import { FormGroup, ButtonGroup, Button, Box, Paper, Typography } from "@mui/material"
import axios from 'axios'
import leds from '@/leds.json'

export default function LEDList() {
  return (
    <Paper sx={{ maxWidth: 400, m: 1, p: 1}}>
      <Typography sx={{ m: 1 }} variant="h6" color="primary" gutterBottom>LED</Typography>
      <FormGroup>
        { leds.map ( led => (
          <Box key={led.pin} >
            <ButtonGroup sx={{ p: 1 }}>
              <Button onClick={
                async () => {
                  try {
                    console.log(`http://${process.env.NEXT_PUBLIC_SERVER_LED}:${process.env.NEXT_PUBLIC_SERVER_LED_PORT}/led/${led.pin}?state=True`)
                    const res = await axios.put(`http://${process.env.NEXT_PUBLIC_SERVER_LED}:${process.env.NEXT_PUBLIC_SERVER_LED_PORT}/led/${led.pin}?state=True`)
                    console.log(res)
                  }
                  catch (e) { console.error(e) }
                }
              }> ON </Button>
              <Button onClick={
                async () => {
                  try {
                    const res = await axios.put(`http://${process.env.NEXT_PUBLIC_SERVER_LED}:${process.env.NEXT_PUBLIC_SERVER_LED_PORT}/led/${led.pin}?state=False`)
                    console.log(res)
                  }
                  catch (e) { console.error(e) }
                }
              } color='error'> OFF </Button>
            </ButtonGroup>
            {led.name}
          </Box>
        ))}
      </FormGroup>
    </Paper>
  )
}