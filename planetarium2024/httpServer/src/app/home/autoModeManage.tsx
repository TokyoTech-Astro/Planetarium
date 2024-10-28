import { ButtonGroup, Button, Paper, Typography } from '@mui/material'
import StopButton from '@/app/home/stopButton'
import axios from 'axios'

export default function AutoModeManage() {
  const onClick = async () => {
    try {
      const res = await axios.post(`http://${process.env.NEXT_PUBLIC_SERVER_HTTP}:${process.env.NEXT_PUBLIC_SERVER_HTTP_PORT}/api/autoMode?query=start`)
      console.log(res)
    }
    catch (e) { console.error(e) }
  }

  return (
    <Paper sx={{ maxWidth: 400, m: 1, p: 1}}>
      <Typography sx={{ m: 1 }} variant="h6" color="primary" gutterBottom>上映</Typography>
      <ButtonGroup sx={{ m: 1 }}>
        <Button variant="contained" onClick={onClick}>上映開始</Button>
        <StopButton />
      </ButtonGroup>
    </Paper>
  )
}