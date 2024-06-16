"use client"

import * as React from 'react';
import {Box} from '@mui/material';
import LEDList from '@/app/home/ledManage';
import AutoModeManage from '@/app/home/autoModeManage';
import MotorManage from '@/app/home/motorManage';

export default function Home() {
  return (
    <Box sx={{ p:1, border: '1px dashed grey' }}>
      <AutoModeManage />
      <LEDList />
      <MotorManage />
    </Box>
  );
}