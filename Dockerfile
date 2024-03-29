FROM python:3.6
ENV PYTHONUNBUFFERED 1
ADD requirements.txt /app/
WORKDIR /app
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN mkdir -p src/asset/video
ADD . /app/

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]