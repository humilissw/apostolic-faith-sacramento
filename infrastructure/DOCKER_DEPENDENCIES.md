# Docker Dependencies

[TOC]

## todo: add rest of instructions here
[todo]

# Deploying the application to an apache container

## Run the dependencies

```pwsh
    cd infrastructure/db
    docker-compose -f .\compose.db.yml  up -d --build
```

## Instructions for Windows

```pwsh
    cd src/fe
    bun run build
    robocopy .\out\ ..\..\infrastructure\db\public_app\ /e
```

## Viewing the site

Navigate to localhost:8080 and the site will be deployed to the root of the site.
