# Trinity

A bot for sending reports and moderating AltAmino.

## Getting Started

### Option 1 — Docker (recommended)

```bash
git clone -b starter https://github.com/altamino/trinity.git
cd trinity
cp .env.example .env   # fill in your variables
docker compose up -d
```

### Option 2 — run directly

```bash
git clone https://github.com/altamino/trinity.git
cd trinity
cp .env.example .env   # fill in your variables
pip install -r requirements.txt
python main.py
```

## Branches

| Branch | Description |
|---|---|
| `main` | source code |
| `starter` | ready-to-deploy server starter |