FROM ubuntu:22.04

# Set DEPLOY=1 environnement variable
ENV DEPLOY=1

# Install dependencies
RUN apt-get update
RUN apt-get upgrade -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y git python3 python3-pip tzdata libmysqlclient-dev

# Add an user
RUN useradd -ms /bin/bash workshop

# Set the PATH to include /home/workshop/.local/bin
ENV PATH="/home/workshop/.local/bin:${PATH}"

# RUN git clone https://github.com/Yaya-Cout/Upsilon-Workshop-API-Django
# We directly copy the files from the parent directory
COPY . Upsilon-Workshop-API-Django

# Change the owner of the files
RUN chown -R workshop:workshop Upsilon-Workshop-API-Django

# Run as the user
USER workshop

# RUN cd Upsilon-Workshop-API-Django
WORKDIR Upsilon-Workshop-API-Django
RUN pip3 install -r requirements.txt gunicorn
# RUN python3 manage.py migrate
RUN python3 manage.py collectstatic --noinput

# Replace `ALLOWED_HOSTS: list[str] = []` with `ALLOWED_HOSTS: list[str] = ["0.0.0.0"]` in `workshop/settings.py`
RUN sed -i 's/ALLOWED_HOSTS: list\[str\] = \[\]/ALLOWED_HOSTS: list\[str\] = \["*"\]/g' workshop/settings.py

# Expose the port
EXPOSE 80

# Entrypoint
CMD ["bash", "-c", "./deploy/prepare_run.sh && gunicorn workshop.wsgi --bind 0.0.0.0:80"]
