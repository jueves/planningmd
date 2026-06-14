FROM python:3.14-trixie

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 libjpeg-dev libopenjp2-7-dev libffi-dev

WORKDIR /planningmd

COPY *.py requirements.txt styles.css .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3001

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "3001"] 
