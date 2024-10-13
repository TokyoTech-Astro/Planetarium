"use client"

import * as React from 'react';
import { Box, createTheme, ThemeProvider, CssBaseline, IconButton } from '@mui/material';
import { Bedtime, BrightnessLow } from '@mui/icons-material';
import LEDList from '@/app/home/ledManage';
import AutoModeManage from '@/app/home/autoModeManage';
import MotorManage from '@/app/home/motorManage';

export default function Home() {
  const [darkMode, setDarkMode] = React.useState<boolean>(true);
  const handleDarkModeOn = () => setDarkMode(true)
  const handleDarkModeOff = () => setDarkMode(false)

  const theme = createTheme({
    palette: {
      mode: darkMode ? "dark" : "light"
    }
  });

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ p:1 }}>
        {darkMode ? (
          <IconButton>
            <Bedtime onClick={handleDarkModeOff} />
          </IconButton>
        ) : (
          <IconButton>
            <BrightnessLow onClick={handleDarkModeOn} />
          </IconButton>
        )}
        <AutoModeManage />
        <LEDList />
        <MotorManage />
      </Box>
    </ThemeProvider>
  );
}