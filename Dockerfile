# Use an official Python runtime as a parent image
FROM python:3.10 as base

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY setup.py .
RUN pip install .

# Copy the rest of the application code
COPY . .

EXPOSE 8080

#FROM base as develop
# Run main.py when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]



