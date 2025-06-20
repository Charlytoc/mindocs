import socketio
from server.utils.printer import Printer

printer = Printer("SOCKET_MANAGER")

class SocketEventsManager(socketio.AsyncNamespace):

    async def on_connect(self, sid, environ):
        printer.info(f"👀 Client {sid} connected")

    async def on_join_case(self, sid, data):
        case_id = data.get("case_id", None)
        if not case_id:
            printer.error(
                f"👀 Client {sid} tried to join case but no case_id was provided"
            )
            return

        printer.info(f"👀 Client {sid} joined case {case_id}")
        # Usa await y enter_room para rooms
        await self.enter_room(sid, f"case_{case_id}")

    async def on_disconnect(self, sid):
        printer.info(f"👀 Client {sid} disconnected")
