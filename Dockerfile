FROM python:3.9

WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code into the container
COPY . .

# Set environment variables
ENV YOUR_REAL_DEBRID_API_KEY=your_api_key
ENV YOUR_BOT_TOKEN=your_bot_token

# Run the bot
CMD ["python", "main.py"]
