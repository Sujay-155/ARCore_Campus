# Start from the standard, non-slim Python 3.10 image
FROM python:3.10

# Set environment variables for specific, compatible versions
ENV CHROME_VERSION="114.0.5735.90-1"
ENV CHROMEDRIVER_VERSION="114.0.5735.90"

# Set the working directory
WORKDIR /app

# Install system libraries, Chrome, and the matching Chromedriver
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates fonts-liberation libnss3 libgconf-2-4 \
    libx11-6 libx11-xcb1 libxss1 libxtst6 libxrandr2 libgbm1 wget unzip \
    && wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb \
    && apt-get install -y ./google-chrome-stable_${CHROME_VERSION}_amd64.deb \
    && wget https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip \
    && unzip chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm google-chrome-stable_${CHROME_VERSION}_amd64.deb chromedriver-linux64.zip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "600", "app:app"]
