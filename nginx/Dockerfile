# Use an official NGINX image as a parent image
FROM nginx:1.21.4

RUN touch /etc/nginx/nginx.conf

# Copy the NGINX configuration file into the container at /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80 for NGINX
EXPOSE 80

# Start NGINX when the container launches
CMD ["nginx", "-g", "daemon off;"]

