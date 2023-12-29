FROM python:3.9

WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code into the container
COPY . .

# Set environment variables
ENV YOUR_REAL_DEBRID_API_KEY=
ENV YOUR_BOT_TOKEN=
# Run the bot
CMD ["python", "uploader.py"]
