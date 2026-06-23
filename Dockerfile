FROM python:3.9.6-slim
WORKDIR /app

ARG GITHUB_TOKEN

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

RUN git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN git config --global --unset url."https://${GITHUB_TOKEN}@github.com/".insteadOf || true

COPY . .
CMD ["python", "main.py"]