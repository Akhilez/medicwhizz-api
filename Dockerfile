FROM python:3.6
WORKDIR /MedicWhizzWeb
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV PORT 8000
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 medicwhizz_web.wsgi:application
