import { Box, ButtonGroup, Button } from '@mui/material'
import StopButton from '@/app/home/stopButton'

export default function AutoModeManage() {
  return (
    <Box sx={{ m: 1, p: 1, border: '3px solid grey', maxWidth: 320 }}>
        <ButtonGroup>
          <Button variant="contained">上映開始</Button>
          <StopButton />
        </ButtonGroup>
    </Box>
  )
}