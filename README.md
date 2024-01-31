`Python` `Django` `Django Rest Framework` `Docker` `Gunicorn` `NGINX` `PostgreSQL` `Yandex Cloud`

# Foodgram Webservice

Foodgram is a diploma project from the Yandex Practicum Python Backend course designed for food enthusiasts to share and discover recipes. The project is built using practical, industry-standard tools to provide a straightforward and effective user experience.

## Technical Overview

- Backend: **Django (Python)**
- Frontend: **React**
- Server: **Gunicorn with Nginx**
- Deployment: **Docker**

## Key Features

- **Recipe Sharing:** Post your recipes for others to enjoy.
- **Favorites:** Save recipes you love for easy access later.
- **Shopping Cart:** Add ingredients to your cart and download a shopping list with one click.
- **Subscriptions:** Follow other users and see their recipes conveniently on a dedicated page.

## Features

- API Endpoint: `/api/` - Access the recipe data.
- Admin Interface: `/admin/` - Manage the platform (demo login: `admin@email.com` / `Gfhjkm12345`)

## Access

Try Foodgram at: https://myfoodgram.zapto.org/

---

## Local Installation Guide

Explore Foodgram on your local machine by following these steps:

1. Clone the repository:
```bash
git@github.com:thehallowedfire/foodgram-project-react.git
```
2. Navigate into the directory:
```bash
cd foodgram-project-react
```
3. Rename `demo.env` file into `.env`. Populate it with your data (optional; do not change `DB_HOST` and `DB_PORT` values).
4. Navigate into `infra` directory:
```bash
cd infra
```
5. Compose Docker container (Docker should be installed on your local machine):
```bash
docker compose up
```
6. Apply migrations (in a separate Bash window navigate to the same folder and follow the next steps):
```bash
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```
7. Import ingredients:
```bash
docker cp ./data infra-backend-1://../backend_static
docker compose exec backend python manage.py add_ingredients
```
8. Create **superuser**:
```bash
docker compose exec backend python manage.py createsuperuser
```
9. Enter [admin zone](http://localhost:7000/admin/) with admin credentials (you just created it)
10. Create 3 tags.
11. Now you can explore the site on http://localhost:7000/

## Author
Vladislav Kondrashov
[GitHub](https://github.com/thehallowedfire/)
[Telegram](https://t.me/kondrashov_vlad)