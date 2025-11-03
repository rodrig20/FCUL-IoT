FROM python:3.13-slim

WORKDIR /app

# Copy dependencies file and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Command default
CMD ["waitress-serve", "--listen=0.0.0.0:5000", "main:app"]
