FROM sitespeedio/webbrowsers:chrome-66-firefox-61-beta-1

RUN sudo apt-get update && sudo apt-get install curl \
  git -y && \
  curl -O https://storage.googleapis.com/golang/go1.9.linux-amd64.tar.gz && \
  tar -xvf go1.9.linux-amd64.tar.gz && \
  sudo mv go /usr/local

ENV PATH="/usr/local/go/bin:${PATH}"

RUN go get github.com/urfave/cli && \
  go get golang.org/x/net/http2 && \
  go get github.com/catapult-project/catapult/web_page_replay_go/src/webpagereplay


COPY build.py /build.py
COPY start.sh /start.sh

ENTRYPOINT ["/build.py"]
