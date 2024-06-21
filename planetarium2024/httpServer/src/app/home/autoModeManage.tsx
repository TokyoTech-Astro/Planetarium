import { Box, ButtonGroup, Button } from '@mui/material'
import StopButton from '@/app/home/stopButton'
import axios from 'axios'

export default function AutoModeManage() {
  const onClick = async () => {
    try { const res = await axios.post('http://pi-controller.local:3000/api/autoMode') }
    catch (e) { console.log(e) }
  }

  return (
    <Box sx={{ m: 1, p: 1, border: '3px solid grey', maxWidth: 320 }}>
        <ButtonGroup>
          <Button variant="contained" onClick={onClick}>上映開始</Button>
          <StopButton />
        </ButtonGroup>
    </Box>
  )
}