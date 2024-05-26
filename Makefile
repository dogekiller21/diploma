
certs:
	docker-compose run certbot certonly --webroot --webroot-path=/var/www/certbot -d $(domain) -d www.$(domain) --email $(email) --agree-tos --no-eff-email --server https://acme-v02.api.letsencrypt.org


start-dev:
	docker-compose -f docker-compose-dev.yaml up

stop-dev:
	docker-compose -f docker-compose-dev.yaml down

start-prod:
	docker-compose up -d

stop-prod:
	docker-compose down
