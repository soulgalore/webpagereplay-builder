FROM sitespeedio/webbrowsers:chrome-81.0-firefox-75.0-c

# The current build.py Need python 2.7 to build
# It's a modified version of https://chromium.googlesource.com/catapulttelemetry/bin/update_wpr_go_binary

RUN sudo apt-get update && sudo apt-get install curl \
  git -y && \
  curl -O https://storage.googleapis.com/golang/go1.17.6.linux-amd64.tar.gz && \
  tar -xvf go1.17.6.linux-amd64.tar.gz && \
  sudo mv go /usr/local

ENV PATH="/usr/local/go/bin:${PATH}"
 
RUN git clone https://chromium.googlesource.com/catapult
RUN  pip install six
COPY build.py /build.py
ENTRYPOINT ["/build.py"]
