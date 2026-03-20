import asyncio
import websockets
import json
import base64
import requests
import socket

RELAY_URL = "ws://xx.xx.xx.xx:8765"  # Укажите белый IP WebSocket Relay
DEVICE_ID = "blazer-1"

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

async def handler():
    print(f"🔌 Подключение к {RELAY_URL}...")

    try:
        async with websockets.connect(RELAY_URL) as ws:
            print("✅ WebSocket подключен!")

            # отправляем регистрацию
            register_msg = {
                "type": "register",
                "deviceId": DEVICE_ID,
                "localIp": get_local_ip(),
                "timestamp": asyncio.get_event_loop().time()
            }
            await ws.send(json.dumps(register_msg))
            print(f"📤 Отправлена регистрация: {DEVICE_ID}")

            # ждем сообщение от RELAY
            async for message in ws:
                print(f"📨 Получено сообщение от relay: {message[:200]}...")  # Логируем первые 200 символов

                try:
                    req = json.loads(message)

                    # Проверяем, что это HTTP-запрос (должен быть requestId)
                    if "requestId" not in req:
                        print(f"⚠️ Сообщение без requestId: {req.get('type', 'unknown')}")
                        continue

                    print(f"📥 HTTP запрос: {req.get('method')} {req.get('url')}")

                    # обрабатываем запрос
                    try:
                        body = base64.b64decode(req.get("body", "")) if req.get("body") else None

                        # Здесь может быть запрос к локальному веб-серверу
                        # Если нет локального сервера — возвращаем тестовый ответ

                        # ВАРИАНТ 1: Если есть локальный веб-сервер
                        # resp = requests.request(
                        #     method=req["method"],
                        #     url=f"http://localhost:80{req['url']}",
                        #     headers=req["headers"],
                        #     data=body,
                        #     timeout=10
                        # )

                        # ВАРИАНТ 2: Тестовый ответ (если нет локального сервера)
                        test_response = {
                            "status": "ok",
                            "device": DEVICE_ID,
                            "method": req.get("method"),
                            "url": req.get("url"),
                            "message": "Hello from device behind NAT!",
                            "timestamp": asyncio.get_event_loop().time()
                        }

                        response = {
                            "requestId": req["requestId"],
                            "status": 200,
                            "headers": {"Content-Type": "application/json"},
                            "body": base64.b64encode(json.dumps(test_response).encode()).decode()
                        }

                        # Если используете вариант с requests, раскомментируйте:
                        # response = {
                        #     "requestId": req["requestId"],
                        #     "status": resp.status_code,
                        #     "headers": dict(resp.headers),
                        #     "body": base64.b64encode(resp.content).decode()
                        # }

                    except Exception as e:
                        print(f"❌ Ошибка обработки: {e}")
                        response = {
                            "requestId": req["requestId"],
                            "status": 500,
                            "headers": {},
                            "body": base64.b64encode(str(e).encode()).decode()
                        }

                    # 4. ОТПРАВЛЯЕМ ОТВЕТ
                    await ws.send(json.dumps(response))
                    print(f"📤 Ответ отправлен для {req['requestId']}")

                except json.JSONDecodeError as e:
                    print(f"❌ Ошибка парсинга JSON: {e}")
                    print(f"   Получено: {message[:200]}")

    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print(f"📱 Агент для устройства: {DEVICE_ID}")
    print(f"🔗 Relay-сервер: {RELAY_URL}")
    print("=" * 50)
    asyncio.run(handler())(venv)
