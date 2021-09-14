FROM sitespeedio/webbrowsers:chrome-81.0-firefox-75.0-c

RUN sudo apt-get update && sudo apt-get install curl \
  git -y && \
  curl -O https://storage.googleapis.com/golang/go1.14.2.linux-amd64.tar.gz && \
  tar -xvf go1.14.2.linux-amd64.tar.gz && \
  sudo mv go /usr/local

ENV PATH="/usr/local/go/bin:${PATH}"

RUN go get github.com/catapult-project/catapult/web_page_replay_go || true
COPY go.mod /root/go/src/github.com/catapult-project/catapult/web_page_replay_go/src/
RUN  pip install six
COPY build.py /build.py
COPY start.sh /start.sh

ENTRYPOINT ["/build.py"]
