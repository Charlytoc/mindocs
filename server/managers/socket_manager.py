import socketio
from server.utils.printer import Printer

printer = Printer("SOCKET_MANAGER")

class SocketEventsManager(socketio.AsyncNamespace):

    async def on_connect(self, sid, environ):
        printer.info(f"👀 Client {sid} connected")

    async def on_join_workflow(self, sid, data):
        workflow_id = data.get("workflow_id", None)
        if not workflow_id:
            printer.error(
                f"👀 Client {sid} tried to join workflow but no workflow_id was provided"
            )
            return

        printer.info(f"👀 Client {sid} joined workflow {workflow_id}")
        # Usa await y enter_room para rooms
        await self.enter_room(sid, f"workflow_{workflow_id}")

    async def on_disconnect(self, sid):
        printer.info(f"👀 Client {sid} disconnected")
