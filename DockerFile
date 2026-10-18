# Playwright publishes images with Python AND browser system deps preinstalled.
# A bare python:3.12-slim would lack the ~30 Linux libraries Chromium needs
# and fail at runtime with "Host system is missing dependencies".
# The tag MUST match the playwright version pinned in requirements.txt.
FROM mcr.microsoft.com/playwright/python:v1.63.0-noble

WORKDIR /app

# Dependencies first, so this layer caches. Editing code won't re-run pip.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Only Chromium keeps the image small; base image already has system deps.
RUN playwright install chromium

# Code last - this layer changes most often.
COPY . .

RUN mkdir -p reports

# Exec form (JSON array) so signals reach pytest for clean shutdown.
CMD ["pytest", "-v"]