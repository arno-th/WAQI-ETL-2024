# Use the official Airflow image as the base
FROM apache/airflow:2.10.2

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the Python packages listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
