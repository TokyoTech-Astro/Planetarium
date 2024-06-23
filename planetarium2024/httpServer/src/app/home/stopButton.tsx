import React from 'react'
import { Button, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions } from '@mui/material'
import axios from 'axios';

export default function StopButton() {
    const [open, setOpen] = React.useState(false);
  
    const handleClickOpen = () => {
      setOpen(true);
    };
  
    const handleClose = () => {
      setOpen(false);
    };

    const handleStop = async () => {
      try {
        const res = await axios.post('http://pi-controller.local:3000/api/autoMode?query=stop')
        console.log(res)
      }
      catch (e) { console.error(e) }
      handleClose()
    }
  
    return (
      <React.Fragment>
        <Button variant="contained" color="error" onClick={handleClickOpen}>
          強制終了
        </Button>
        <Dialog
          open={open}
          onClose={handleClose}
        >
          <DialogTitle>
            {"⚠本当に終了しますか？⚠"}
          </DialogTitle>
          <DialogContent>
            <DialogContentText>
              「一時停止」ではなく「終了」です。再開することはできません。
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>いいえ</Button>
            <Button onClick={handleStop}>はい</Button>
          </DialogActions>
        </Dialog>
      </React.Fragment>
    );
  }