# Stage 1: Install wkhtmltox dependencies
FROM ubuntu:22.04 AS builder
RUN apt-get update && apt-get install -y \
    wget \
    fontconfig \
    libfreetype6 \
    libjpeg-turbo8 \
    libpng16-16 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    xfonts-75dpi \
    xfonts-base \
    libssl3 \
    && apt-get clean
# Download wkhtmltox
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb -O /wkhtmltox.deb

# Stage 2: Build the final image
FROM ubuntu:22.04
# Copy wkhtmltox from builder stage
COPY --from=builder /wkhtmltox.deb /wkhtmltox.deb
# Install wkhtmltox and other necessary packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    fontconfig \
    libfreetype6 \
    libjpeg-turbo8 \
    libpng16-16 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    xfonts-75dpi \
    xfonts-base \
    libssl3 \
    && dpkg -i /wkhtmltox.deb \
    && apt-get -f install -y \
    && rm /wkhtmltox.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
# Set working directory
WORKDIR /app
# Copy application code
COPY . /app
# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Create necessary directories and set ownership and permissions
RUN mkdir -p /app/input /app/output /app/logs /app/data \
    && chown -R 1000:1000 /app/input /app/output /app/logs /app/data

# Set the entrypoint to the CLI script
ENTRYPOINT ["python3", "cli.py"]
# Expose the input and output directories as volumes
VOLUME ["/app/input", "/app/output"]