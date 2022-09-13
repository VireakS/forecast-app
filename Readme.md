# Installations
- `copy sample.env.dev .env.dev`
- `docker-compose build`
- `docker-compose up`
- listen `localhost:5000`

# Command
- migrate database
`docker-compose exec web python manage.py migrate`
- seed database
`docker-compose exec web python manage.py seed_db`


# Error
- Error permission
`chmod +x services/web/entrypoint.sh`
