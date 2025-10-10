# Askbrain Tilda Top Posts

Python-сервис для периодической выгрузки топ-3 постов из Tilda feed и обновления JSON-файлов в репозитории.

## Локальный запуск

```bash
poetry install
poetry run askbrain-cli fetch-top
```

Настройте переменные среды:

- `ORIGIN_HOST` — Origin сайта Tilda
- `TILDA_FEED_UIDS` — список feed UID через запятую
- `TILDA_REC_ID` — recid страницы
- `TILDA_SIZE` — размер страницы (по умолчанию 100)
- `TILDA_CONCURRENCY` — количество параллельных запросов

## GitHub Actions

Workflow `.github/workflows/hourly-top-posts.yml` запускается ежечасно и сохраняет JSON.

### Secrets

- `ORIGIN_HOST`
- `TILDA_FEED_UIDS`
- `TILDA_REC_ID`
- `GH_TOKEN` — токен с правами `repo` для пуша

### Variables (опционально)

- `TILDA_SIZE`
- `TILDA_CONCURRENCY`

