import { TextField, Button, MenuItem, FormGroup} from "@mui/material"
import axios from "axios"
import React from "react"

export default function MotorManage() {
  const onSubmit = async (formData: FormData) => {
    const deg: number = Number(formData.get("degree"))
    if(deg >= 0) await axios.post(`http://pi-controller.local:8000/motor?dir=forward&deg=${deg}&speed=${speed}`)
    else if(deg < 0) await axios.post(`http://pi-controller.local:8000/motor?dir=back&deg=${-deg}&speed=${speed}`)
  }

  const [speed, setSpeed] = React.useState<string>("");

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
        <TextField
          sx={{ m: 1, width: 120, minWidth: 120 }}
          value={speed}
          onChange={e => setSpeed(e.target.value)}
          select
          label="スピード"
          required
        >
          <MenuItem value="low"> 低 </MenuItem>
          <MenuItem value="medium"> 中 </MenuItem>
          <MenuItem value="high"> 高 </MenuItem>
        </TextField>
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