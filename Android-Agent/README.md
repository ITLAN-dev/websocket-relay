# WebSocket Relay Agent — Android клиент для удаленного доступа к устройствам за NAT


## 📱 Описание

**WebSocket Relay Agent** — это Android-приложение, которое подключается к relay-серверу через WebSocket и проксирует HTTP-запросы к локальному веб-интерфейсу устройства. Позволяет получить удаленный доступ к устройству за NAT без настройки проброса портов.

### Возможности
- ✅ Автоматическое подключение к relay-серверу
- ✅ Регистрация устройства с уникальным ID
- ✅ Heartbeat для поддержания соединения
- ✅ Автоматическое переподключение при обрыве связи
- ✅ Работа в фоне (Foreground Service)
- ✅ Обработка HTTP-запросов от relay-сервера
- ✅ Отправка ответов обратно через WebSocket

---

## 🏗️ Как это работает

```
┌─────────────────┐                    ┌─────────────────────────────────────┐
│   Интернет      │                    │      Relay-сервер                   │
│                 │                    │      (Python/Go)                    │
│  ┌───────────┐  │                    │                                     │
│  │  Клиент   │  │   HTTP запрос      │  ┌─────────────────────────────┐   │
│  │  (curl,   │──┼───────────────────▶│  │      HTTP API :8080         │   │
│  │   браузер)│  │                    │  └─────────────┬───────────────┘   │
│  └───────────┘  │                    │                │                    │
│                 │                    │                │ WebSocket         │
│                 │                    │                │ (постоянное       │
│                 │                    │                │  соединение)      │
│                 │                    │                ▼                    │
│                 │                    │     ┌──────────────────────┐       │
│                 │                    │     │   Android Agent      │       │
│                 │                    │     │   (ваше приложение)  │       │
│                 │                    │     │                      │       │
│                 │                    │     │  • Подключение       │       │
│                 │                    │     │  • Регистрация       │       │
│                 │                    │     │  • Heartbeat         │       │
│                 │                    │     └──────────────────────┘       │
└─────────────────┘                    └─────────────────────────────────────┘
```

**Поток данных:**
1. Приложение на Android подключается к relay-серверу по WebSocket
2. Отправляет регистрацию с `deviceId` и локальным IP
3. Регулярно отправляет heartbeat для поддержания соединения
4. При получении HTTP-запроса от relay, обрабатывает его и отправляет ответ
5. Если соединение потеряно — автоматически переподключается

---

## 📋 Требования

- **Android 7.0 (API 24)** и выше
- **Интернет-соединение**
- **Relay-сервер** (Python/Go) с белым IP

---

## 🔧 Установка

### Скачать APK
1. Скачайте последнюю версию APK из [репозитория](https://URL)
2. Скопируйте на телефон
3. Разрешите установку из неизвестных источников
4. Установите приложение

---

## 🚀 Использование

### 1. Запустите relay-сервер
```bash
python relay.py
```

### 2. Настройте приложение
- Откройте приложение на Android
- Введите URL relay-сервера: `ws://xx.xx.xx.xx:8765`
- Введите ID устройства: `android-device-1`
- Нажмите **"Запустить агента"**

### 3. Проверьте подключение
```bash
curl http://xx.xx.xx.xx:8080/device/android-device-1/test
```

Ожидаемый ответ:
```json
{
    "status": "ok",
    "device": "android-device-1",
    "method": "GET",
    "url": "/test",
    "message": "I'm a device for NAT, tune me !!!",
    "timestamp": 1742500000
}
```

---

## 📁 Структура проекта

```
WebSocketRelayAgent/
├── app/
│   ├── src/main/
│   │   ├── java/com/itlan/relayagent/
│   │   │   ├── MainActivity.kt          # Главная активность
│   │   │   ├── RelayService.kt          # Foreground Service
│   │   │   └── models/
│   │   │       └── Models.kt            # Модели данных
│   │   ├── res/
│   │   │   ├── layout/
│   │   │   │   └── activity_main.xml    # Интерфейс
│   │   │   └── values/
│   │   │       ├── strings.xml
│   │   │       ├── colors.xml
│   │   │       └── themes.xml
│   │   └── AndroidManifest.xml
│   └── build.gradle.kts
├── build.gradle.kts
└── settings.gradle.kts
```

---

## 🔧 Настройка AndroidManifest.xml

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />

<service
    android:name=".RelayService"
    android:exported="false"
    android:foregroundServiceType="dataSync" />
```

---

## 🛠️ Зависимости (build.gradle.kts)

```kotlin
dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.11.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    
    // WebSocket
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    
    // JSON
    implementation("com.google.code.gson:gson:2.10.1")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
}
```

---

## 🐛 Устранение неполадок

### Проблема: Приложение падает при запуске
**Решение:** Проверьте `AndroidManifest.xml` — добавьте `foregroundServiceType="dataSync"` в service.

### Проблема: Нет подключения к relay-серверу
**Решение:**
1. Проверьте, что relay-сервер запущен
2. Проверьте URL: должен быть `ws://IP:8765` (не `http://`)
3. Проверьте, что телефон имеет доступ к интернету
4. Проверьте логи: `adb logcat | grep RelayService`

### Проблема: Приложение не видит устройство в Android Studio
**Решение:**
1. Включите режим разработчика на телефоне
2. Включите отладку по USB
3. Установите Google USB Driver

### Проблема: Ошибка "foregroundServiceType"
**Решение:** В `AndroidManifest.xml` добавьте:
```xml
<service android:name=".RelayService"
         android:foregroundServiceType="dataSync" />
```

---

## 📊 Логирование

### Просмотр логов через adb
```bash
# Все логи приложения
adb logcat | grep com.itlan.relayagent

# Только ошибки
adb logcat *:E | grep relayagent

# Сохранить в файл
adb logcat -d > logcat.txt
```

### Логи в приложении
```
I/RelayService: Service onCreate
I/RelayService: 🔌 Подключение к ws://xx.xx.xx.xx:8765
I/RelayService: ✅ WebSocket подключен!
I/RelayService: 📤 Отправлена регистрация: android-device-1 (IP: 192.168.xx.xx)
I/RelayService: 🎉 Регистрация подтверждена
```

---

## 📄 Лицензия

(Добавить)

Copyright (c) 2026 ITLAN

(Добавить)

---

## 🤝 Контакты

**ITLAN**     
- 🌐 Сайт: [https://github.com/ITLAN-dev](https://github.com/ITLAN-dev)

---

<div align="center">
  
**Разработано ITLAN | 2026**

</div>
