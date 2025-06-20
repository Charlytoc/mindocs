import { io, Socket } from "socket.io-client";

class SocketClient {
  private socket: Socket;

  constructor(host: string) {
    console.log("starting client socket", host);
    this.socket = io(host, {
      autoConnect: false,
    });
  }

  connect() {
    this.socket.connect();
  }

  disconnect() {
    this.socket.disconnect();
  }
  on(event: string, callback: (...args: any[]) => void) {
    this.socket.on(event, callback);
  }

  off(event: string) {
    this.socket.off(event);
  }

  emit(event: string, ...args: any[]) {
    this.socket.emit(event, ...args);
  }
}

export default new SocketClient("");
