FROM python:3.7-alpine

RUN apk --update add --no-cache bash tzdata build-base libffi-dev openssl-dev

WORKDIR .

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "app.py" ]
