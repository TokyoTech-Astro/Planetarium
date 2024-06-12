"use client"

import * as React from 'react';
import {Box} from '@mui/material';
import LEDList from './ledList';
import AutomodeManage from './automodeManage';
import MotorManage from './motorManage';

export default function Home() {
  return (
    <Box sx={{ p:1, border: '1px dashed grey' }}>
      <AutomodeManage />
      <LEDList />
      <MotorManage />
    </Box>
  );
}
