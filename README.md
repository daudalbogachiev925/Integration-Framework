# Integration-Framework
Описание: фреймворк интеграций 1С с внешними системами: HTTP-сервисы, очереди, retry, circuit breaker, идемпотентность, мониторинг.
# Integration Framework для 1С

Фреймворк интеграций с внешними системами.

## Компоненты
- HTTP client с retry + circuit breaker
- File queue (producer/consumer, ack/nack)
- Idempotency store (дедупликация)
- Monitor (counters, timers, p95)
- Adapters: REST, CRM, WMS

## Запуск
```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
pytest -v
```
