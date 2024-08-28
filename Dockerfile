FROM python:3.12.3-alpine

ENV PYTHONUNBUFFERED=1 COLUMNS=200 \
    TZ=Asia/Almaty \
    # Poetry's configuration:
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local' \
    POETRY_VERSION=1.8.3

COPY poetry.lock pyproject.toml /src/

# User local alpine repositories
RUN sed -i "s/dl-cdn.alpinelinux.org/mirror.neolabs.kz/g" \
    /etc/apk/repositories \
    && apk update \
    && apk --no-cache add bash \
# Add build dependencies
    && apk --no-cache add --virtual .build-deps \
    gcc \
# Set timezone
    && ln -fs /usr/share/zoneinfo/Asia/Almaty /etc/localtime \
    && echo "Asia/Almaty" > /etc/timezone \
# Upgrade pip
    && pip install --upgrade pip setuptools wheel \
# Install poetry
    && pip install --no-cache-dir poetry==${POETRY_VERSION} \
# Add project dependencies
    && poetry install --directory=/src --no-interaction --no-ansi \
# Remove build dependencies
    && apk del .build-deps

# Copy src:
COPY ./src /src

WORKDIR /src

# Run proccess:
CMD ["./entrypoint.sh"]
