# Контрольная работа №3 Суринов Артём ЭФБО-03-24

## Установка зависимостей

```bash
pip install fastapi uvicorn passlib bcrypt pyjwt slowapi python-dotenv
```

## Очистка портов

```bash
for port in 8001 8002 8003 8004 8005 8007 8008 8009; do
  lsof -ti:$port | xargs kill -9 2>/dev/null
done
```

---

## Задание 6.1

### Запуск
```bash
cd task_6_1 && python main.py
```

### Тестирование
```bash
curl -u admin:secret123 http://localhost:8001/login
```

---

## Задание 6.2

### Запуск
```bash
cd task_6_2 && python main.py
```

### Тестирование
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"pass123"}' \
  http://localhost:8002/register

curl -u user1:pass123 http://localhost:8002/login
```

---

## Задание 6.3

### Запуск
```bash
cd task_6_3 && python main.py
```

### Тестирование
```bash
curl -u admin:secret123 http://localhost:8003/docs
curl http://localhost:8003/
```

---

## Задание 6.4

### Запуск
```bash
cd task_6_4 && python main.py
```

### Тестирование
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"john","password":"doe"}' \
  http://localhost:8004/login

curl -H "Authorization: Bearer TOKEN" http://localhost:8004/protected_resource
```

---

## Задание 6.5

### Запуск
```bash
cd task_6_5 && python main.py
```

### Тестирование
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"qwerty123"}' \
  http://localhost:8005/register

curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"qwerty123"}' \
  http://localhost:8005/login

curl -H "Authorization: Bearer TOKEN" http://localhost:8005/protected_resource
```

---

## Задание 7.1

### Запуск
```bash
cd task_7_1 && python main.py
```

### Тестирование
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  http://localhost:8007/register

curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  http://localhost:8007/login

curl -X POST -H "Authorization: Bearer TOKEN" http://localhost:8007/admin/resource
curl -H "Authorization: Bearer TOKEN" http://localhost:8007/user/resource
```

---

## Задание 8.1

### Запуск
```bash
cd task_8_1 && python main.py
```

### Тестирование
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"12345"}' \
  http://localhost:8008/register
```

---

## Задание 8.2

### Запуск
```bash
cd task_8_2 && python main.py
```

### Тестирование
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"title":"Buy milk","description":"Go to store"}' \
  http://localhost:8009/todos

curl http://localhost:8009/todos
curl http://localhost:8009/todos/1

curl -X PUT -H "Content-Type: application/json" \
  -d '{"completed":true}' \
  http://localhost:8009/todos/1

curl -X DELETE http://localhost:8009/todos/1
```
