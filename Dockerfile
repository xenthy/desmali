FROM ubuntu:20.10

# set up apktool
RUN apt update -y && apt install -y --no-install-recommends \
    python3.8 \
    python3-pip \
    apktool \
    zipalign \
    apksigner

# Directory for the program
WORKDIR /ict2207

# Install dependencies
COPY requirements.txt .
RUN pip3 install --quiet --no-cache-dir -r requirements.txt

# Cleanup
RUN \
    apt remove -y &&\
    apt clean && \
    apt autoclean && \
    apt autoremove -y
# rm -rf /var/lib/apt/lists/* /tmp/* > /dev/null 2>&1

# Copy source code
COPY / /ict2207

# For flask
EXPOSE 8000

# Run the program
CMD ["python3", "src/main.py"]
# CMD ["/bin/bash"]
