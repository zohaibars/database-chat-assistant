# Use the specified base image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

# Set timezone
ENV TZ="UTC"

# Set work Directory
WORKDIR /app/

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy pyproject.toml and poetry.lock to docker
COPY ./pyproject.toml ./poetry.lock* /app/

# Install only main dependencies
RUN poetry install --no-root --no-dev

# Copy the rest of the application files
COPY . /app

# Copy .env file
COPY .env /app/.env

# Set Python path
ENV PYTHONPATH=/app

# Expose port for communication
EXPOSE 8080
