"use client"

import * as React from 'react';
import Box from '@mui/material/Box';
import Switch from '@mui/material/Switch';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button'
import ButtonGroup from '@mui/material/ButtonGroup'
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';

export function AlertDialog() {
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

export default function Home() {
  return (
    <Box sx={{ p:1, border: '1px dashed grey' }}>
      <Box sx={{ p: 1, border: '1px dashed grey' }}>
        <ButtonGroup variant="contained">
          <Button>上映開始</Button>
          <AlertDialog />
        </ButtonGroup>
      </Box>
      <FormGroup
        sx={{ p: 2, border: '1px dashed grey' }}
      >
        <FormControlLabel control={<Switch />} label="恒星" />
        <FormControlLabel control={<Switch />} label="一等星" />
        <FormControlLabel control={<Switch />} label="さそり座" />
        <FormControlLabel control={<Switch />} label="ペガサス座" />
        <FormControlLabel control={<Switch />} label="おおいぬ座" />
        <FormControlLabel control={<Switch />} label="こいぬ座" />
        <FormControlLabel control={<Switch />} label="こぐま座" />
        <FormControlLabel control={<Switch />} label="おりおん座" />
        <FormControlLabel control={<Switch />} label="いて座" />
      </FormGroup>
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
    </Box>
  );
}
