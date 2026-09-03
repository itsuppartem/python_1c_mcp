English | [Русский](#russkiy)

# python-1c-mcp

[![PyPI](https://img.shields.io/pypi/v/python-1c-mcp.svg)](https://pypi.org/project/python-1c-mcp/)
[![Python versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://github.com/itsuppartem/python_1c_mcp)
[![CI](https://github.com/itsuppartem/python_1c_mcp/actions/workflows/test.yml/badge.svg)](https://github.com/itsuppartem/python_1c_mcp/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/itsuppartem/python_1c_mcp/blob/main/LICENSE)

Read-only [Model Context Protocol](https://modelcontextprotocol.io/) server for **1C:Enterprise standard OData** (`standard.odata`, platform **8.3.5+**).

Built on [python-1c-odata](https://github.com/itsuppartem/python_1c_odata). Exposes schema discovery and OData queries to LLM agents in Claude Desktop, Cursor, and other MCP hosts.

Homepage / repo: https://github.com/itsuppartem/python_1c_mcp

## Read-only scope

This server provides **read-only** access only:

- List and describe entity sets from `$metadata`
- Query entity sets (`$filter`, `$select`, `$top`, `$skip`, `$orderby`, `$inlinecount`)
- Fetch a single record by `Ref_Key`

There are **no** create, update, delete, post, or unpost tools.

**Honest limits:** standard OData 3.0 publication only. No 8.2, 7.7, SOAP, COM, or proprietary APIs. Oldest publication is 8.3.5 Atom (`ONEC_FORMAT=atom` or `auto`). JSON is the default (`8.3.6+`).

## Install

```bash
pip install python-1c-mcp
```

Python 3.10+. Depends on `python-1c-odata` 0.6.0+ and `mcp` 2.0+. From a clone:

```bash
git clone https://github.com/itsuppartem/python_1c_mcp.git
cd python_1c_mcp
pip install -e ".[dev]"
```

## Connect to 1C

This server talks to a **published standard OData** interface on 1C:Enterprise **8.3.5+**. It does not open Designer, the thick/thin client, SOAP `/ws/`, custom HTTP services (`/hs/`), COM, 8.2, or 7.7. If OData is not published, there is no other way for this MCP to “log into 1C”.

On the 1C side:

1. Publish the infobase on the web server (Apache or IIS) from Designer: **Administration → Publish on web server**.
2. Enable the standard OData interface for that publication (`enableStandardOData` / the OData checkbox). The service path is `/odata/standard.odata`.
3. Create or pick a user who is allowed to use that publication (HTTP Basic). This is the web-service login, not an interactive Designer session.

URL shape from the four variables:

`{ONEC_SERVER}/{ONEC_INFOBASE}/odata/standard.odata`

Example: `ONEC_SERVER=http://1c.example`, `ONEC_INFOBASE=trade` → `http://1c.example/trade/odata/standard.odata`.

8.3.5 publications speak Atom only — set `ONEC_FORMAT=atom` (or `auto`). 8.3.6+ can use the default JSON.

Auth is HTTP Basic: `ONEC_USER` / `ONEC_PASSWORD` (or `user:pass@` inside `ONEC_URL`). Then add the MCP JSON below in Cursor or Claude Desktop.

## Connection (environment variables)

| Variable | Required | Description |
|----------|----------|-------------|
| `ONEC_SERVER` | Yes* | Server base URL, e.g. `http://1c.example` |
| `ONEC_INFOBASE` | Yes* | Publication name, e.g. `trade` |
| `ONEC_USER` | Yes* | OData user |
| `ONEC_PASSWORD` | Yes* | OData password |
| `ONEC_URL` | Alt. | Single URL: `http://user:pass@host/publication` (overrides the four vars above) |
| `ONEC_FORMAT` | No | Response format: `json` (default), `atom`, or `auto` |
| `ONEC_DEBUG` | No | If `true` / `1` / `yes` / `on`, log HTTP requests to stderr |

\* Either set `ONEC_URL` **or** all four of `ONEC_SERVER`, `ONEC_INFOBASE`, `ONEC_USER`, `ONEC_PASSWORD`.

The server validates configuration at startup and exits with a clear stderr message if settings are missing.

## MCP configuration

### Claude Desktop / Cursor

```json
{
  "mcpServers": {
    "1c-odata": {
      "command": "python",
      "args": ["-m", "python_1c_mcp.server"],
      "env": {
        "ONEC_SERVER": "http://1c.example",
        "ONEC_INFOBASE": "trade",
        "ONEC_USER": "odata_user",
        "ONEC_PASSWORD": "secret"
      }
    }
  }
}
```

Alternatively, use the console script:

```json
{
  "mcpServers": {
    "1c-odata": {
      "command": "python-1c-mcp",
      "env": {
        "ONEC_URL": "http://odata_user:secret@1c.example/trade"
      }
    }
  }
}
```

## Tools

| Tool | Parameters | Description |
|------|------------|-------------|
| `list_entity_sets` | — | All entity set names from `$metadata` (truncated after 500) |
| `describe_entity_set` | `entity_set` | Keys, properties, navigation for one set (e.g. `Catalog_Товары`) |
| `odata_query` | `entity_set`, `odata_filter`, `select`, `top`, `skip`, `orderby`, `inlinecount` | Read-only collection query. `top` default 20, max 100 |
| `get_entity` | `entity_set`, `ref_key`, `select` | Single record by `Ref_Key` GUID |
| `get_metadata` | `raw_xml` | Summary (count + sample names) or truncated raw `$metadata` XML |

## Resources

| URI | Description |
|-----|-------------|
| `1c://entity-sets` | Plain-text list of entity set names |
| `1c://metadata` | `$metadata` XML (truncated if large) |

## What is still missing

| Missing | Notes |
| --- | --- |
| Write tools | no create / edit / delete / post / unpost — this package is read-only |
| 8.2 / 7.7 / SOAP / COM / `/hs/` / OData 4 | out of scope. Oldest publication we speak is 8.3.5 Atom |

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check src tests
mypy src
```

## License

MIT — Artem Gulyaev

---

<h2 id="russkiy">Русский</h2>

# python-1c-mcp

[English](#python-1c-mcp) | Русский

[![PyPI](https://img.shields.io/pypi/v/python-1c-mcp.svg)](https://pypi.org/project/python-1c-mcp/)
[![Python versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://github.com/itsuppartem/python_1c_mcp)
[![CI](https://github.com/itsuppartem/python_1c_mcp/actions/workflows/test.yml/badge.svg)](https://github.com/itsuppartem/python_1c_mcp/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/itsuppartem/python_1c_mcp/blob/main/LICENSE)

Сервер [Model Context Protocol](https://modelcontextprotocol.io/) **только для чтения** стандартного OData **1С:Предприятие** (`standard.odata`, платформа **8.3.5+**).

Собран на [python-1c-odata](https://github.com/itsuppartem/python_1c_odata). Отдаёт агентам LLM в Claude Desktop, Cursor и других MCP-хостах схему и запросы OData.

Репозиторий: https://github.com/itsuppartem/python_1c_mcp

## Область только чтения

Сервер даёт доступ **только на чтение**:

- Список и описание наборов сущностей из `$metadata`
- Запросы к наборам (`$filter`, `$select`, `$top`, `$skip`, `$orderby`, `$inlinecount`)
- Одна запись по `Ref_Key`

Инструментов создания, изменения, удаления, проведения и отмены проведения **нет**.

**Честные границы:** только стандартная публикация OData 3.0. Нет 8.2, 7.7, SOAP, COM и закрытых API. Самая старая публикация — Atom 8.3.5 (`ONEC_FORMAT=atom` или `auto`). По умолчанию JSON (`8.3.6+`).

## Установка

```bash
pip install python-1c-mcp
```

Нужен Python 3.10+. Зависимости: `python-1c-odata` 0.6.0+ и `mcp` 2.0+. Из клона:

```bash
git clone https://github.com/itsuppartem/python_1c_mcp.git
cd python_1c_mcp
pip install -e ".[dev]"
```

## Подключение к 1С

Сервер ходит в **опубликованный стандартный OData** на 1С:Предприятие **8.3.5+**. Он не открывает Конфигуратор, толстый/тонкий клиент, SOAP `/ws/`, произвольные HTTP-сервисы (`/hs/`), COM, 8.2 и 7.7. Если OData не опубликован, другим способом «войти в 1С» этот MCP не умеет.

На стороне 1С:

1. Опубликуйте информационную базу на веб-сервере (Apache или IIS) из Конфигуратора: **Администрирование → Публикация на веб-сервере**.
2. Включите стандартный интерфейс OData у этой публикации (`enableStandardOData` / флажок OData). Путь сервиса — `/odata/standard.odata`.
3. Заведите или выберите пользователя с правом на эту публикацию (HTTP Basic). Это логин веб-сервиса, не интерактивный сеанс Конфигуратора.

Форма URL из четырёх переменных:

`{ONEC_SERVER}/{ONEC_INFOBASE}/odata/standard.odata`

Пример: `ONEC_SERVER=http://1c.example`, `ONEC_INFOBASE=trade` → `http://1c.example/trade/odata/standard.odata`.

Публикации 8.3.5 говорят только Atom — задайте `ONEC_FORMAT=atom` (или `auto`). С 8.3.6 можно оставить JSON по умолчанию.

Авторизация — HTTP Basic: `ONEC_USER` / `ONEC_PASSWORD` (или `user:pass@` внутри `ONEC_URL`). Затем добавьте JSON MCP ниже в Cursor или Claude Desktop.

## Подключение (переменные окружения)

| Переменная | Обязательна | Описание |
|------------|-------------|----------|
| `ONEC_SERVER` | Да* | Базовый URL сервера, например `http://1c.example` |
| `ONEC_INFOBASE` | Да* | Имя публикации, например `trade` |
| `ONEC_USER` | Да* | Пользователь OData |
| `ONEC_PASSWORD` | Да* | Пароль OData |
| `ONEC_URL` | Альтернатива | Один URL: `http://user:pass@host/publication` (перекрывает четыре переменные выше) |
| `ONEC_FORMAT` | Нет | Формат ответа: `json` (по умолчанию), `atom` или `auto` |
| `ONEC_DEBUG` | Нет | Если `true` / `1` / `yes` / `on`, HTTP-запросы пишутся в stderr |

\* Задайте либо `ONEC_URL`, **либо** все четыре: `ONEC_SERVER`, `ONEC_INFOBASE`, `ONEC_USER`, `ONEC_PASSWORD`.

Сервер проверяет настройки при старте и выходит с понятным сообщением в stderr, если чего-то не хватает.

## Настройка MCP

### Claude Desktop / Cursor

```json
{
  "mcpServers": {
    "1c-odata": {
      "command": "python",
      "args": ["-m", "python_1c_mcp.server"],
      "env": {
        "ONEC_SERVER": "http://1c.example",
        "ONEC_INFOBASE": "trade",
        "ONEC_USER": "odata_user",
        "ONEC_PASSWORD": "secret"
      }
    }
  }
}
```

Либо консольный скрипт:

```json
{
  "mcpServers": {
    "1c-odata": {
      "command": "python-1c-mcp",
      "env": {
        "ONEC_URL": "http://odata_user:secret@1c.example/trade"
      }
    }
  }
}
```

## Инструменты

| Инструмент | Параметры | Описание |
|------------|-----------|----------|
| `list_entity_sets` | — | Все имена наборов из `$metadata` (обрезка после 500) |
| `describe_entity_set` | `entity_set` | Ключи, свойства, навигация одного набора (например `Catalog_Товары`) |
| `odata_query` | `entity_set`, `odata_filter`, `select`, `top`, `skip`, `orderby`, `inlinecount` | Запрос коллекции только на чтение. `top` по умолчанию 20, максимум 100 |
| `get_entity` | `entity_set`, `ref_key`, `select` | Одна запись по GUID `Ref_Key` |
| `get_metadata` | `raw_xml` | Сводка (число + примеры имён) или обрезанный XML `$metadata` |

## Ресурсы

| URI | Описание |
|-----|----------|
| `1c://entity-sets` | Текстовый список имён наборов |
| `1c://metadata` | XML `$metadata` (обрезается, если большой) |

## Чего нет

| Нет | Комментарий |
| --- | --- |
| Инструменты записи | нет create / edit / delete / post / unpost — пакет только для чтения |
| 8.2 / 7.7 / SOAP / COM / `/hs/` / OData 4 | вне задачи. Самая старая публикация — Atom 8.3.5 |

## Разработка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check src tests
mypy src
```

## Лицензия

MIT — Артём Гуляев
