import { FormGroup, ButtonGroup, Button, Box } from "@mui/material"
import axios from 'axios'
import leds from '@/leds.json'

export default function LEDList() {
  return (
    <FormGroup
      sx={{ p: 1, border: '1px dashed grey' }}
    >
      { leds.map ( led => (
        <Box sx={{ border: '1px dashed grey' }} key={led.pin}>
          <ButtonGroup sx={{ p: 1, border: '1px dashed grey' }}>
            <Button onClick={
              async () => {
                const response = await axios.put(`http://pi-starsphere:8000/led/${led.pin}?state=True`)
              }
            }> ON </Button>
            <Button onClick={
              async () => {
                const response = await axios.put(`http://pi-starsphere:8000/led/${led.pin}?state=False`)
              }
            } color='error'> OFF </Button>
          </ButtonGroup>
          {led.name}
        </Box>
      ))}
    </FormGroup>
  )
}