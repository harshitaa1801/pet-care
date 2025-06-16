FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV APP_ROOT /app
ENV CONFIG_ROOT /config
    
WORKDIR ${APP_ROOT}

# Install Python dependencies
RUN mkdir ${CONFIG_ROOT}
COPY requirements.txt ${CONFIG_ROOT}/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r ${CONFIG_ROOT}/requirements.txt

# Copy project files
COPY . ${APP_ROOT}
RUN chmod +x ${APP_ROOT}/wsgi-entrypoint.sh
RUN chmod +x ./wsgi-entrypoint.sh

# Run the entrypoint
ENTRYPOINT ["/app/wsgi-entrypoint.sh"]
