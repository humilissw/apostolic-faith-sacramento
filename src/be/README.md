# Backend

## Prerequisites

- Setup Poetry by running the setup_poetry.py script.

## Helpful Reading

- https://fastapi.tiangolo.com/async/#asynchronous-code

## FastAPI

The backend uses FastAPI.

## Poetry

Poetry is a tool for dependency management and packaging in python.

https://python-poetry.org/docs/#installation
https://python-poetry.org/docs/basic-usage/
https://python-poetry.org/docs/managing-environments/#activating-the-environment

---
This section is a work in progress.

### Windows

1. First install [scoop](https://scoop.sh/).

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
```

1. Then install [pipx](https://github.com/pypa/pipx?tab=readme-ov-file#on-windows).

```powershell
scoop install pipx
pipx ensurepath
```

1. Then install [poetry](https://python-poetry.org/docs/#installing-with-pipx).

```powershell
pipx install poetry
```

1. Finally, ensure you close all terminals/instances of Visual Studio Code (vscode) so you don't have issues with your path.

* If you need to upgrade, merely run: `pipx upgrade poetry`.
* If you need to uninstall: `pipx uninstall poetry`.

1. Then install the dependencies:

```shell
> cd src/be/afcapp_root
## activate the virtual env
> Invoke-Expression (poetry env activate)
# install the project dependencies
> poetry install
## run the app - no ssl
# > poetry run uvicorn app.main:app --reload
## run the app - with SSL (required now)
> poetry run uvicorn app.main:app --reload --ssl-certfile=../../infrastructure/certs/cert.pem --ssl-keyfile=../../infrastructure/certs/key.pem
```

### Mac/Linux

```shell
## setup poetry
> python3 setup_poetry.py
## activate the virtual env
> Invoke-Expression (poetry env activate)
## run the app
> poetry run fastapi dev main.py
```

# Housekeeping stuff
