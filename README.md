# KUMM - Aplikacja do zarządzania przychodnią lekarską

## Jak uruchomić kod 

0. Wymagania wstępne
```zsh
    git clone https://github.com/mjkur/kumm-final.git
    cd kumm
``` 

1. Docker (jeśli posiadasz Dockera i Docker Compose):
```zsh
    docker compose up
```

2. Python:
```zsh
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    python manage.py runserver
```

