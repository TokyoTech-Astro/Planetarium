import { Box, ButtonGroup, Button } from '@mui/material'
import StopButton from '@/app/Home/stopButton'

export default function AutomodeManage() {
  return (
    <Box sx={{ p: 1, border: '1px dashed grey' }}>
        <ButtonGroup variant="contained">
          <Button>上映開始</Button>
          <StopButton />
        </ButtonGroup>
    </Box>
  )
}