# **Аттестационная работа Потаенко Анны - чат бот напоминаний**

### Проверить бота можно тут: t.me/potanya_bot

### Развёртывание:
1. Скачать последний релиз (именно релиз)
2. Установить переменные среды в docker-compose файле 
3. Запустить docker-compose up --build

### Главные фичи:
- Бот шифрует все напоминания в базе данных, что обеспечивает их конфиденциальность.
- Бот воспринимает время напоминания в любом формате (завтра, через 3 дня, 2024-12-12 в три часа дня)
- Бот написан с использованием асинхронной библиотеки aiogram.
- Бот напоминает о событии заранее и ждет подтверждения прочтения от человека.
- Если поддтверждения нету, бот будет напоминать снова и снова.