FROM python:3.14-slim

WORKDIR /planningmd

COPY *.py requirements.txt styles.css .

RUN pip install --no-cache-dir requirements.txt

EXPOSE 3001

CMD ["python", "api.py"] 
