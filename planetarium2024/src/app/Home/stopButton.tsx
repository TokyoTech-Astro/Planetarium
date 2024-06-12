import React from 'react'
import { Button, Dialog, DialogTitle, DialogContent, DialogContentText, DialogActions } from '@mui/material'

export default function StopButton() {
    const [open, setOpen] = React.useState(false);
  
    const handleClickOpen = () => {
      setOpen(true);
    };
  
    const handleClose = () => {
      setOpen(false);
    };
  
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
            <Button onClick={handleClose} autoFocus color='error'>いいえ</Button>
            <Button onClick={handleClose} variant='outlined' color='error'>はい</Button>
          </DialogActions>
        </Dialog>
      </React.Fragment>
    );
  }