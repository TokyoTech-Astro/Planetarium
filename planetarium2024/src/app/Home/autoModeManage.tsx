import { Box, ButtonGroup, Button } from '@mui/material'
import StopButton from '@/app/home/stopButton'

export default function AutoModeManage() {
  return (
    <Box sx={{ p: 1, border: '1px dashed grey' }}>
        <ButtonGroup>
          <Button variant="contained">上映開始</Button>
          <StopButton />
        </ButtonGroup>
    </Box>
  )
}