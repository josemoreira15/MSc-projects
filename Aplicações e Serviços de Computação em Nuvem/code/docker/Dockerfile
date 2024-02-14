# Dockerfile for the laravel.io application
FROM ubuntu:22.04

ENV seed_database false
ENV migrate true
ENV delete_data false

ENV COMPOSER_ALLOW_SUPERUSER=1

ENV TZ=Europe/Lisbon
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get upgrade -y && \
    apt-get install software-properties-common -y

RUN add-apt-repository ppa:ondrej/php && apt-get update && apt-get install -y \
    php8.2 \
    php8.2-curl \
    php8.2-simplexml \
    php8.2-dom \
    php8.2-zip \
    php8.2-mysql \
    npm \
    mysql-server \
    nodejs \
    curl \
    git \
    composer

RUN git clone https://github.com/laravelio/laravel.io.git
WORKDIR /laravel.io

RUN npm install -g n && n latest
RUN npm i vite
RUN npm run build

RUN composer install

RUN cp .env.example .env

RUN php artisan key:generate

# Copy start script
COPY ./script.sh .

# Add execution permission to start script
RUN chmod +x script.sh

# Expose port 8000
EXPOSE 8000

# Start Swap server
ENTRYPOINT ["./script.sh"]