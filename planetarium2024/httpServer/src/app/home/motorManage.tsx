import { Box, TextField, Button } from "@mui/material"

export default function MotorManage() {
  return (
    <form>
      <Box
        sx={{ border: '1px dashed grey' }}
        display="flex"
        alignItems="center"
      >
        <TextField
          sx={{ m: 1, border: '1px dashed grey', width: 400 }}
          label="回転量(度,負の数=時間を戻す)"
        />
        <Button
          variant="contained"
          type="submit"
          sx={{ m: 1, border: '1px dashed grey' }}
        >
          実行
        </Button>
      </Box>
    </form>
  )
}