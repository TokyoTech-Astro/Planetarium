"use client"

import Home from "@/app/Home/page"
import { Button, Switch } from "@mui/material";
import { useState } from "react"

export default function Page() {
  const [_ledState, _setLedState] = useState<boolean>(false)
  const led = {
    state: _ledState,
    setState: _setLedState
  }
  return (
    <Home ledState={led} />
  );
}
