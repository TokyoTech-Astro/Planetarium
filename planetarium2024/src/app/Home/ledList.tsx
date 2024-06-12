import { FormGroup, FormControlLabel, Switch } from "@mui/material"
import leds from '@/LEDs.json'

export default function LEDList() {
  return (
    <FormGroup
      sx={{ p: 2, border: '1px dashed grey' }}
    >
      { leds.map ( led => (
        <FormControlLabel control={<Switch />} label={led.name} key={led.pin} />
      ))}
    </FormGroup>
  )
}