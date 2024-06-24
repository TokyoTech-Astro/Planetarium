import { TextField, Button, MenuItem, FormGroup, ToggleButton, ToggleButtonGroup} from "@mui/material"
import axios from "axios"
import React from "react"

export default function MotorManage() {
  const onSubmit = async (formData: FormData) => {
    const deg: number = Number(formData.get("degree"))
    if(deg >= 0) {
      try {
        const res = await axios.post(`http://pi-controller.local:8000/motor?query=start&dir=forward&deg=${deg}&speed=${speed}`)
        console.log(res)
      }
      catch (e) { console.error(e) }
    }
    else if(deg < 0) {
      try {
        const res = await axios.post(`http://pi-controller.local:8000/motor?query=start&dir=back&deg=${-deg}&speed=${speed}`)
        console.log(res)
      }
      catch (e) { console.error(e) }
    }
  }

  const [speed, setSpeed] = React.useState<string>("");

  const handleChange = (
    event: React.MouseEvent<HTMLElement>,
    value: string
  ) => {
    setSpeed(value);
  };

  return (
    <form action={onSubmit}>
      <FormGroup sx={{ m: 1, p: 1, border: '3px solid grey', maxWidth: 320 }}>
        <TextField
          sx={{ m: 1, width: 300, minWidth: 300 }}
          label="回転量(度,負の数=時間を戻す)"
          name="degree"
          type="number"
          required
        />
        <ToggleButtonGroup
          sx={{ m: 1 }}
          color="primary"
          exclusive
          value={speed}
          onChange={handleChange}
        >
          <ToggleButton value="low">低速</ToggleButton>
          <ToggleButton value="medium">中速</ToggleButton>
          <ToggleButton value="high">高速</ToggleButton>
        </ToggleButtonGroup>
        <Button
          variant="contained"
          type="submit"
          sx={{ m: 1, maxWidth: 80 }}
        >
          実行
        </Button>
      </FormGroup>
    </form>
  )
}