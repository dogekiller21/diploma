FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY config/nginx-dev.conf /etc/nginx/conf.d/nginx.conf