FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app


RUN pip install playwright==1.40.0 playwright-stealth tzdata

COPY scraper.py .

RUN mkdir -p /app/data

CMD ["python", "scraper.py"]