"use client"

import * as React from 'react';
import {Box} from '@mui/material';
import LEDList from '@/app/Home/ledList';
import AutoModeManage from '@/app/Home/autoModeManage';
import MotorManage from '@/app/Home/motorManage';
import ConnectionButton from '@/app/Home/connectButton';

export default function Home() {
  return (
    <Box sx={{ p:1, border: '1px dashed grey' }}>
      <AutoModeManage />
      <LEDList />
      <MotorManage />
      <ConnectionButton />
    </Box>
  );
}
