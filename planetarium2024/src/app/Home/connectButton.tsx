'use client';

import { FormEventHandler } from 'react';
import { io } from 'socket.io-client';

export default function ConnectionButton() {
  const handleSubmit: FormEventHandler<HTMLFormElement> = async (event) => {
    event.preventDefault();
    const socket = io({ autoConnect: false });

    // サーバーとの接続が確立したときの処理
    socket.on('connect', () => {
      console.log('Connected to the server');
    });
    // サーバーとの接続が切断されたときの処理
    socket.on('disconnect', () => {
      console.log('Disconnected from the server');
    });
    // サーバーからメッセージを受信したときの処理
    socket.on('message', (message: string) => {
      console.log(message)
    });

    await fetch('http://localhost:3000/api/webSocket', { method: 'POST' });
    socket.connect();

    socket.emit('message', "message from client to server")
  };

  return (
    <form onSubmit={handleSubmit}>
      <button>Connect</button>
    </form>
  );
}