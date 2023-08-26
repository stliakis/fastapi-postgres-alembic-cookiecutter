FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

WORKDIR /app/

RUN apt-get update
RUN apt-get update && apt-get install -y inotify-tools

RUN pip install --no-cache-dir poetry

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./app/pyproject.toml ./app/poetry.lock* /app/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN poetry config virtualenvs.create false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --only main ; fi"

RUN apt-get update && apt-get install -y inotify-tools

COPY ./app /app

ENV PYTHONPATH=/app

