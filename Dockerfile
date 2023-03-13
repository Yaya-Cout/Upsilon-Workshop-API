FROM alpine:latest AS builder

# Set DEPLOY=1 environnement variable
ENV DEPLOY=1

# Install dependencies
RUN apk update
RUN apk upgrade --available
RUN apk add --no-cache git python3 python3-dev py-pip tzdata mariadb-client mariadb-connector-c-dev gcc musl-dev
RUN pip3 install --upgrade virtualenv wheel

# Add an user
# RUN useradd -ms /bin/bash workshop
RUN adduser -D workshop

# We copy the files from the parent directory
COPY . Upsilon-Workshop-API-Django

# Remove the .git folder
RUN rm -rf Upsilon-Workshop-API-Django/.git

# Change the owner of the files
RUN chown -R workshop:workshop Upsilon-Workshop-API-Django

# Run as the user
USER workshop

WORKDIR Upsilon-Workshop-API-Django

# Create a virtual environment
RUN virtualenv -p python3 venv

# Activate the virtual environment
ENV PATH="/Upsilon-Workshop-API-Django/venv/bin:${PATH}"

# Install the dependencies
RUN pip3 install -r requirements.txt gunicorn

# RUN python3 manage.py migrate
RUN python3 manage.py collectstatic --noinput

# Replace `ALLOWED_HOSTS: list[str] = []` with `ALLOWED_HOSTS: list[str] = ["0.0.0.0"]` in `workshop/settings.py`
RUN sed -i 's/ALLOWED_HOSTS: list\[str\] = \[\]/ALLOWED_HOSTS: list\[str\] = \["*"\]/g' workshop/settings.py

# Expose the port
EXPOSE 80

# Entrypoint
CMD ["sh", "-c", "sh ./deploy/prepare_run.sh && python3 $(which gunicorn) workshop.wsgi --bind 0.0.0.0:8000"]


# Deployment image (no build dependencies)
FROM alpine:latest

# Set DEPLOY=1 environnement variable
ENV DEPLOY=1

# Install dependencies
RUN apk update && apk upgrade --available && apk add --no-cache mariadb-client mariadb-connector-c tzdata python3

# Add an user
RUN adduser -D workshop

# Copy the files from the builder image
COPY --from=builder /Upsilon-Workshop-API-Django /home/workshop/Upsilon-Workshop-API-Django

# Activate the virtual environment
ENV PATH="/home/workshop/Upsilon-Workshop-API-Django/venv/bin:${PATH}"

# Change the owner of the files
RUN chown -R workshop:workshop /home/workshop/Upsilon-Workshop-API-Django

# Run as the user
USER workshop

# Set the working directory
WORKDIR /home/workshop/Upsilon-Workshop-API-Django

# Expose the port
EXPOSE 80

# Entrypoint
CMD ["sh", "-c", "source venv/bin/activate && deactivate && source venv/bin/activate && sh ./deploy/prepare_run.sh && python3 $(which gunicorn) workshop.wsgi --bind 0.0.0.0:8000"]
