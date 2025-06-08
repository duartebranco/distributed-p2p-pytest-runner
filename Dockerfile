FROM python:3.10-slim

# install git + unzip for zip_handler & git clones
RUN apt-get update \
 && apt-get install -y --no-install-recommends git unzip lsof \
 && rm -rf /var/lib/apt/lists/*

# avoid buffering Python output
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=src/main.py

WORKDIR /app

# install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY src/ src/

# copia o script que detecta o IP e inicia o Flask
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# expose default ports (overridden by compose)
EXPOSE 7000 7001

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]