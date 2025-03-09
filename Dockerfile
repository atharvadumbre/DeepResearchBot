# Dockerfile

FROM python:3.10-slim

# Make apt non-interactive
ENV DEBIAN_FRONTEND=noninteractive

# 1) System dependencies for OCR (tesseract + poppler), Chrome, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    unzip \
    tesseract-ocr \
    poppler-utils \
    libmagic-dev \
    # Dependencies often needed for Chrome
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# 2) Install Google Chrome stable
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 3) (Option A from the explanation).
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium-driver

ENV PATH="/usr/local/bin:${PATH}"

# 4) Create a directory for your app code and copy everything
WORKDIR /app
COPY . /app

# 5) Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 6) Expose the default port for Streamlit
EXPOSE 8501

# For Cloud Run, we listen on PORT (default 8080). Streamlit param:
ENV PORT=8080

# 7) The CMD - run Streamlit on the container’s $PORT
CMD sh -c "streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0"
