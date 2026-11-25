## Запуск

### Запит до NVD API

```bash
python -m labs.lab04.main --cve CVE-2021-44228
```

### Завантаження відповіді NVD API із файлу

```bash
python -m labs.lab04.main --cve CVE-2099-10001 --input labs/lab04/data/nvd_sample.json
```

## Автоматизовані тести

Запуск тестів:

```bash
python -m pytest labs/lab04/tests -v
```
