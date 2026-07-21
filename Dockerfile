# Schwab Market Data PySpark Analytics — container image
#
# Base image already includes JDK 17 (Temurin) — the project's stated
# prerequisite. spark.jars.packages fetches the mssql-jdbc driver from
# Maven Central the first time the container runs, so it needs internet
# access on that first run.

FROM eclipse-temurin:17-jdk-jammy

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv python3-pip \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# schwab_market_data_pyspark.ini is intentionally NOT baked into the image —
# mount it as a volume at runtime (see docker-compose.yml).
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
