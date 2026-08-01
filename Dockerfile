FROM python:3.14-trixie

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 libjpeg-dev libopenjp2-7-dev libffi-dev cups-client \
    fontconfig fonts-liberation

# Debian's fonts-noto-color-emoji is a bitmap (CBDT) font that WeasyPrint
# cannot embed in the PDF (emojis come out blank). Use the vector (COLRv1)
# build of Noto Color Emoji served by Google Fonts instead.
ADD https://fonts.gstatic.com/s/notocoloremoji/v39/Yq6P-KqIXTD0t4D9z1ESnKM3-HpFab4.ttf /usr/local/share/fonts/NotoColorEmoji.ttf
RUN chmod 644 /usr/local/share/fonts/NotoColorEmoji.ttf && fc-cache -f

WORKDIR /planningmd

COPY *.py requirements.txt styles.css .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3001

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "3001"] 
