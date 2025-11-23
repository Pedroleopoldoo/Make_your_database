# Use a base image with Python
FROM python:3.12.0

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Copy the entire project directory into the container
COPY . .

# Expose the port Streamlit runs on (default is 8501)
EXPOSE 8500

ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Define the command to run your Streamlit application
ENTRYPOINT ["streamlit", "run"]
CMD ["main.py"]