# Итоговый проект "GigaVibeMiptCode"

Консольный чат-бот для общения с LLM через OpenAI-compatible API.

## Возможности

- чат с LLM;
- история сообщений;
- ограничение контекста по числу сообщений и символов;
- конфигурация через `config.yaml` и переменные окружения;
- streaming response;
- подстановка файлов через `@::filepath::`;
- обработка файлов по чанкам через `/filechunk`;

## Установка

```bash
python -m pip install -r final_project/requirements.txt
```

Для локального запуска через Ollama:

```powershell
irm https://ollama.com/install.ps1 | iex
ollama pull gemma3:270m
```

## Конфигурация

Создайте файл `final_project/config.yaml`:

```yaml
api_key: ollama
api_host: http://localhost:11434/v1/
model: gemma3:270m
limit_message: 20
limit_chars: 2000
temperature: 0.7
system_prompt: You are a helpful assistant.
stream: true
```

## Запуск

Из корня репозитория:

```bash
python final_project/main.py
```


## Команды

```text
\q                         выход
/reset                     очистить историю
/filechunk                 обработать файл по абзацам
/file_chunk                то же самое
/filechunk paragraph=3     по 3 абзаца
/filechunk len=150         по 150 символов
/filechunk len=150 -y      обработать все чанки без подтверждения
```


## Подстановка файлов

```text
Проверь код @::final_project/example.py::
```

## Архитектура

Проект выполнен ак консольное приложение.

```text
final_project/
  main.py       точка входа
  cli.py        консольный интерфейс и команды
  chat.py       состояние сессии, история и подготовка сообщений
  llm.py        OpenAI-compatible клиент
  config.py     загрузка и валидация настроек
  messages.py   представление сообщений
  context.py    ограничение длины контекста
  files.py      подстановка файлов через @::filepath::
  chunks.py     разбиение файлов на чанки
  errors.py     ошибки приложения
