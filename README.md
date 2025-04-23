# Simple Eda Visualize Tool

Simple dash plotly app for EDA visualization

# Requirements

- docker

# Usage

1. Clone the repository

```bash
git clone https://github.com/Maszz/EDA-Tool.git
cd EDA-Tool
```

2. Build the docker image

```bash
docker build -t <image-name> .
```

3. Run the docker container

```bash
docker run -p 8050:80 <image-name>
```

4. Open your browser and go to `http://localhost:8050`

5. Upload your CSV file and start exploring your data!
