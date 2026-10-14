FROM python:3.13-trixie

RUN apt-get update && apt-get install curl \
  git -y && \
  curl -L -O https://go.dev/dl/go1.24.13.linux-amd64.tar.gz && \
  tar -xvf go1.24.13.linux-amd64.tar.gz && \
  mv go /usr/local

ENV PATH="/usr/local/go/bin:${PATH}"

RUN git clone --depth 1 https://chromium.googlesource.com/catapult
RUN git clone https://chromium.googlesource.com/webpagereplay /catapult/web_page_replay_go && \
  cd /catapult/web_page_replay_go && git checkout 7ed888744ce019687980074a909b6588db7da971
RUN pip install six
COPY build.py /build.py
ENTRYPOINT ["/build.py"]
