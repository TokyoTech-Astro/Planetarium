import { FormGroup, ButtonGroup, Button, Box } from "@mui/material"
import axios from 'axios'
import leds from '@/leds.json'

export default function LEDList() {
  return (
    <FormGroup sx={{ m: 1, p: 1, border: '3px solid grey', maxWidth: 320 }}>
      { leds.map ( led => (
        <Box key={led.pin} >
          <ButtonGroup sx={{ p: 1 }}>
            <Button onClick={
              async () => {
                const response = await axios.put(`http://pi-starsphere.local:8000/led/${led.pin}?state=True`)
              }
            }> ON </Button>
            <Button onClick={
              async () => {
                const response = await axios.put(`http://pi-starsphere.local:8000/led/${led.pin}?state=False`)
              }
            } color='error'> OFF </Button>
          </ButtonGroup>
          {led.name}
        </Box>
      ))}
    </FormGroup>
  )
}