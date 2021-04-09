FROM ubuntu:20.10

# Change sources list to use a server in Singapore
RUN sed -i 's/archive.ubuntu.com/mirror.0x.sg/' /etc/apt/sources.list

# Install dependacies
RUN apt-get update -y && apt install -y --no-install-recommends \
    python3.8 \
    python3-pip \
    apktool \
    zipalign \
    apksigner

# Cleanup
RUN \
    apt-get remove -y &&\
    apt-get clean && \
    apt-get autoclean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* /tmp/* > /dev/null 2>&1

# Directory for the program
WORKDIR /ict2207

# Copy requirements.txt
COPY /requirements.txt /ict2207

# Install python dependacies
RUN pip3 install --quiet --no-cache-dir -r requirements.txt

# Copy source code
COPY / /ict2207


# For flask
EXPOSE 6969

# Run the program
# CMD ["python3", "src/main.py"]
CMD ["python3", "src/server.py"]
# CMD ["/bin/bash"]
