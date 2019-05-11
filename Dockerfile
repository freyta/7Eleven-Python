FROM python:3.7-alpine

WORKDIR .

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "app.py" ]
