#!/bin/bash
# tf-backend/scripts/deploy.sh

echo "Starting TrainFair backend deployment..."

# Update system packages
sudo dnf update -y

# Install required system packages
sudo dnf install -y python3-pip nginx certbot python3-certbot-nginx

# Activate virtual environment
source tfenv/bin/activate

# Update dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy systemd serice file
sudo cd deployment/trainfair.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable trainfair
sudo systemctl restart trainfair

# Configure Nginx
sudo cp deployment/nginx.conf /etc/nginx/conf.d/trainfair.conf
sudo nginx -t && sudo systemctl restart nginx

# Setup SSL
sudo certbot --nginx -d trainfair.io -d www.trainfair.io --non-interactive --agree-tos --email info@trainfair.io

echo "Deployment completed!"