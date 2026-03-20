import asyncio
import json
import base64
import uuid
from aiohttp import web
import websockets

agent_ws = None
pending_requests = {}

async def handle_http(request):
    global agent_ws, pending_requests

    if agent_ws is None:
        return web.Response(status=503, text="No agent connected")

    body = await request.read()
    request_id = str(uuid.uuid4())

    payload = {
        "requestId": request_id,
        "method": request.method,
        "url": request.rel_url.path_qs,
        "headers": dict(request.headers),
        "body": base64.b64encode(body).decode() if body else ""
    }

    future = asyncio.get_event_loop().create_future()
    pending_requests[request_id] = future

    await agent_ws.send(json.dumps(payload))
    print(f"📤 Запрос {request_id} отправлен агенту")

    try:
        response = await asyncio.wait_for(future, timeout=30)
        print(f"📥 Ответ {request_id} получен от агента")

        return web.Response(
            status=response.get("status", 200),
            headers=response.get("headers", {}),
            body=base64.b64decode(response.get("body", ""))
        )
    except asyncio.TimeoutError:
        print(f"⏰ Таймаут для запроса {request_id}")
        return web.Response(status=504, text="Gateway Timeout")
    finally:
        if request_id in pending_requests:
            del pending_requests[request_id]

async def ws_handler(websocket):
    global agent_ws
    print("Agent connected")
    agent_ws = websocket

    try:
        async for message in websocket:
            data = json.loads(message)
            request_id = data.get("requestId")

            if request_id and request_id in pending_requests:
                pending_requests[request_id].set_result(data)
                print(f"✅ Ответ от агента для {request_id}")
            else:
                msg_type = data.get("type", "unknown")
                device_id = data.get("deviceId", "unknown")
                print(f"📨 Сообщение от агента: type={msg_type}, deviceId={device_id}")

    except Exception as e:
        print(f"❌ WebSocket ошибка: {e}")
    finally:
        agent_ws = None
        print("Agent disconnected")

async def main():
    # HTTP сервер
    app = web.Application()
    app.router.add_route("*", "/{tail:.*}", handle_http)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    # WebSocket сервер
    ws_server = await websockets.serve(ws_handler, "0.0.0.0", 8765)

    print("=" * 50)
    print("🚀 Relay-сервер запущен")
    print(f"📡 HTTP:  http://0.0.0.0:8080")
    print(f"🔌 WebSocket: ws://0.0.0.0:8765")
    print("=" * 50)

    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
