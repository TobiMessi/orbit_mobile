FROM python:3.11-slim
WORKDIR /app
RUN pip install flask docker werkzeug pyyaml flask-cors
COPY . .
CMD ["python", "app.py"]
