## Build WPR binaries

Build the Docker image and run it to produce WPR binaries for Linux amd64, Linux arm64, and macOS arm64, plus the matching `deterministic.js`, in one go:

```bash
docker build --platform linux/amd64 -t soulgalore/webpagereplaybuilder .
docker run -v "$(pwd)":/output soulgalore/webpagereplaybuilder
```

Output:

```
build/
├── deterministic.js
├── linux/
│   ├── amd64/wpr
│   └── arm64/wpr
└── darwin/
    └── arm64/wpr
```

To change the target platforms, update `_SUPPORTED_PLATFORMS` in **build.py**.

## Pinned dependencies

The [webpagereplay](https://chromium.googlesource.com/webpagereplay) repository is pinned to a specific commit in the Dockerfile to ensure reproducible builds:

```dockerfile
RUN git clone https://chromium.googlesource.com/webpagereplay /catapult/web_page_replay_go && \
  cd /catapult/web_page_replay_go && git checkout <commit>
```

[catapult](https://chromium.googlesource.com/catapult) is cloned at HEAD (`--depth 1`) since only its telemetry Python library is used, and that part changes rarely.

## Updating webpagereplay

1. Find the latest commit hash on the [webpagereplay repository](https://chromium.googlesource.com/webpagereplay):
   ```bash
   git ls-remote https://chromium.googlesource.com/webpagereplay HEAD
   ```
2. Update the commit hash in the `git checkout` line in **Dockerfile**.
3. Rebuild and verify:
   ```bash
   docker build --platform linux/amd64 -t soulgalore/webpagereplaybuilder .
   docker run -v "$(pwd)":/output soulgalore/webpagereplaybuilder
   file build/linux/amd64/wpr build/linux/arm64/wpr build/darwin/arm64/wpr
   ```

## Updating Go

Update the Go version in the `curl` line in **Dockerfile**:

```dockerfile
curl -L -O https://go.dev/dl/go<VERSION>.linux-amd64.tar.gz
```

Check [go.dev/dl](https://go.dev/dl/) for the latest release. After updating, rebuild the image.
