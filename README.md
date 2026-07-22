## Getting Started

Clone this branch, configure your environment variables and launch with Docker:

```bash
git clone -b starter https://github.com/alx0rr/sunset.git
cd sunset
cp .env.example .env   # edit .env
```

### Launch

Just run:
```bash
docker compose up -d
```

Or with auto-update in the background (checks for new image every 60 sec):
```bash
nohup sh update.sh &
```

To stop auto-update:
```bash
kill $(pgrep -f update.sh)
```