FROM python:3.12-slim
LABEL author=igor.mitiukliaev

ARG APP_PORT

ENV \
	PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	LANG=en_US.UTF-8 \
    TZ=Europe/Moscow \
    POETRY_VIRTUALENVS_PATH=/opt/

WORKDIR /opt
RUN pip install poetry==2.2.1
COPY src/poetry.lock /opt/poetry.lock
COPY src/pyproject.toml /opt/pyproject.toml
RUN poetry install
COPY src .

# Применение миграций базы данных на этапе сборки образа
# Примечание: Миграции будут применены при запуске контейнера через command в docker-compose

COPY src/start.sh /opt/start.sh
RUN chmod +x /opt/start.sh

RUN chown -R 1001 /opt/ \
    && chown -R 1001 /var/cache/ \
    && chown -R 1001 /var/run/ \
    && chmod u-s /usr/bin/gpasswd \
    && chmod u-s /bin/su \
    && chmod u-s /bin/mount \
    && chmod g-s /sbin/unix_chkpwd \
    && chmod u-s /usr/bin/chsh \
    && chmod u-s /usr/bin/chfn \
    && chmod u-s /usr/bin/passwd \
    && chmod g-s /usr/bin/chage \
    && chmod g-s /usr/bin/expiry \
    && chmod u-s /bin/umount \
    && chmod g-s /usr/bin/wall \
    && chmod u-s /usr/bin/newgrp

USER 1001

# Миграции будут выполняться через docker-compose command
CMD ["poetry", "run", "python", "-m", "main"]