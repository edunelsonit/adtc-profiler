FROM python:3.12-slim

WORKDIR /app
COPY server.py index.html app.js styles.css tutor.css ./

# GembuGo serves only local static files and has no Python package dependencies.
ENV PORT=8000
EXPOSE 8000

CMD ["python3", "server.py"]
