#!/bin/bash

sed -ri "s/^DB_DATABASE=.*/DB_DATABASE=${DB_DATABASE}/g" .env
sed -ri "s/^DB_USERNAME=.*/DB_USERNAME=${DB_USERNAME}/g" .env
sed -ri "s/^DB_PASSWORD=.*/DB_PASSWORD=${DB_PASSWORD}/g" .env

if [[ $migrate == "true" ]] && [[ -z $MIGRATE_COUNTER ]]; then
  echo ">>> Running migration"
  php artisan migrate
  export MIGRATE_COUNTER=1
fi

sleep 30

if [[ $seed_database == "true" ]] && [[ -z $SEED_COUNTER ]]; then
  echo ">>> Seeding Database"
  php artisan db:seed
  export SEED_COUNTER=1
fi

echo ">>> Starting app..."
php artisan serve --host=0.0.0.0