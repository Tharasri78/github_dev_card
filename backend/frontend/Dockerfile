FROM nginx:alpine

# Default value for envsubst to work if not provided
ENV BACKEND_URL="http://localhost:8080"

COPY index.html /usr/share/nginx/html/

# Replace the environment variables in index.html before starting Nginx
CMD envsubst '${BACKEND_URL}' < /usr/share/nginx/html/index.html > /usr/share/nginx/html/index.tmp.html && mv /usr/share/nginx/html/index.tmp.html /usr/share/nginx/html/index.html && nginx -g 'daemon off;'

EXPOSE 80
