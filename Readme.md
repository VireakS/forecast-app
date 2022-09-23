## Installation
1. create `.env.dev`
`cp `
2. run docker build
`docker-compose build`
3. run docker up
`docker-compose up`
4. migrations
`docker-compose exec web python manage.py makemigrations`
5. migrate
`docker-compose exec web python manage.py migrate`
6. create superuser
`docker-compose exec web python manage.py createsuperuser`