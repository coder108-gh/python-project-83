

### Hexlet tests and linter status:
[![Actions Status](https://github.com/coder108-gh/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/coder108-gh/python-project-83/actions)



# Page Analyzer

Page Analyzer – приложение для веб. Написано на Python (Flask/PostgreSQL). Проверяет URL сайтов на доступность и собирает в базу данных значения (при их наличии) тегов h1 и title, а так же атрибута description тега meta.  

## Demo
URL:[Page Analyzer](https://python-project-83-wlr5.onrender.com)

## How To

### Install Dependencies
```bash
make install
```

### Create a database
```bash
psql -d <database_name> -f database.sql
```

### Start
```bash
make start
```
