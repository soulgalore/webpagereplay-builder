FROM python:3.11.7-bullseye

# The current build.py Need python 2.7 to build
# It's a modified version of https://chromium.googlesource.com/catapulttelemetry/bin/update_wpr_go_binary

RUN apt-get update && apt-get install curl \
  git -y && \
  curl -O https://storage.googleapis.com/golang/go1.21.11.linux-amd64.tar.gz && \
  tar -xvf go1.21.11.linux-amd64.tar.gz && \
  mv go /usr/local

ENV PATH="/usr/local/go/bin:${PATH}"
 
RUN git clone https://chromium.googlesource.com/catapult
RUN pip install six
COPY build.py /build.py
COPY modified/go.mod /catapult/web_page_replay_go/go.mod
COPY modified/transformers.go /catapult/web_page_replay_go/src/webpagereplay/transformers.go
ENTRYPOINT ["/build.py"]
