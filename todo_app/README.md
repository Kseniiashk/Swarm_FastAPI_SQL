# Todo API with Docker Swarm

Проект реализует микросервис для управления задачами с использованием FastAPI, MySQL и Docker Swarm. 

## Технологии
- FastAPI (Python 3.9)
- MySQL 8.0
- Docker Swarm
- JWT аутентификация
- Automatic failover


## Примеры запросов

### 1. Аутентификация
**Регистрация пользователя**:
```bash
curl -X POST "http://localhost:8000/register/" \
  -H "Content-Type: application/json" \
  -d '{"username":"user1", "email":"user1@example.com", "password":"pass123"}'
```

**Получение токена**:
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/token/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=user1&password=pass123" | jq -r '.access_token')
```

---

### 2. Работа с задачами (CRUD)
**Создание задачи**:
```bash
curl -X POST "http://localhost:8000/tasks/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Сделать ДЗ по Docker",
    "description":"Задание по ИПР",
    "priority":1,
    "tags":["учеба", "срочно"]
  }'
```

**Получение всех задач**:
```bash
curl -X GET "http://localhost:8000/tasks/" \
  -H "Authorization: Bearer $TOKEN"
```

**Фильтрация по тегу**:
```bash
curl -X GET "http://localhost:8000/tasks/?tag=учеба" \
  -H "Authorization: Bearer $TOKEN"
```

**Обновление задачи** (ID=1):
```bash
curl -X PUT "http://localhost:8000/tasks/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Обновленное задание",
    "priority":2,
    "is_completed":true
  }'
```

**Удаление задачи** (ID=1):
```bash
curl -X DELETE "http://localhost:8000/tasks/1" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 3. Статистика
**Получение статистики**:
```bash
curl -X GET "http://localhost:8000/tasks/stats/" \
  -H "Authorization: Bearer $TOKEN"
```
Пример ответа:
```json
{
  "total_tasks": 5,
  "completed_tasks": 3,
  "pending_tasks": 2,
  "tasks_by_priority": {
    "high": {"count": 2, "tasks": [...]},
    "medium": {"count": 2, "tasks": [...]},
    "low": {"count": 1, "tasks": [...]}
  }
}
```

---

### 4. Проверка здоровья
```bash
curl -X GET "http://localhost:8000/health"
```
Ответ:
```json
{"status":"OK","database":"connected"}
```

---

### 5. Демонстрация сохранения данных
```bash
# Создаем задачу
curl -X POST "http://localhost:8000/tasks/" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Проверка volume"}'

# Останавливаем БД
docker-compose stop db

# Запускаем заново
docker-compose up -d db

# Проверяем сохранение
curl -X GET "http://localhost:8000/tasks/" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 6. Swarm-режим
**Имитация отказа**:
```bash
docker service update --force todo_web
docker service ps todo_web  # Проверяем перезапуск
```

**Проверка реплик**:
```bash
docker service inspect --pretty todo_web
```

## Swagger UI
```
http://localhost:8000/docs
```

## Документация про команды
```
http://localhost:8000/redoc
```

## Healthcheck
Система мониторинга доступна по:
```
http://localhost:8000/health
```

## Примечания
- Все запросы требуют JWT аутентификации
- Данные сохраняются при любых перезапусках
- Swarm обеспечивает отказоустойчивость
