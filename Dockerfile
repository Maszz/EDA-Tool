
# Stage 1: Build Cython extensions
FROM python:3.12.2-slim AS build

# Set the working directory for the build
WORKDIR /app

# Install build dependencies (e.g., build-essential, Cython, make)
RUN apt-get update && apt-get install -y \
    build-essential \
    cython3 \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (Cython is needed for building the Cython extensions)
RUN pip install --no-cache-dir cython numpy

# Copy the project files into the build container
COPY . /app

# Navigate to the C library directory and run `make build` and `make install`
WORKDIR /app/clib
RUN make build 

# Stage 2: Final production image
FROM python:3.12.2-slim AS production

# Set the working directory for the app
WORKDIR /app

# Copy only the necessary files from the build stage (avoids unnecessary build files in the final image)
COPY --from=build /app /app

RUN apt-get update && apt-get install -y \
    cython3 \
    make \
    && rm -rf /var/lib/apt/lists/*


# Install the necessary Python packages (e.g., Dash, Plotly)
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --no-cache-dir cython

# Run make install in the production stage to ensure libraries are available
WORKDIR /app/clib
# RUN make install
RUN pip install .
# Expose the port your Dash app will run on (default is 8050)
EXPOSE 80
WORKDIR /app
# Define the command to run your app
# CMD ["python", "app.py"]
CMD gunicorn -b 0.0.0.0:80 app:server

