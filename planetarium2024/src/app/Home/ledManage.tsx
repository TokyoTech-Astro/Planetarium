import { FormGroup, ButtonGroup, Button, Box } from "@mui/material"
import leds from '@/LEDs.json'

export default function LEDList() {
  return (
    <FormGroup
      sx={{ p: 1, border: '1px dashed grey' }}
    >
      { leds.map ( led => (
        <Box sx={{ border: '1px dashed grey' }} key={led.pin}>
          <ButtonGroup sx={{ p: 1, border: '1px dashed grey' }}>
            <Button> ON </Button>
            <Button color='error'> OFF </Button>
          </ButtonGroup>
          {led.name}
        </Box>
      ))}
    </FormGroup>
  )
}