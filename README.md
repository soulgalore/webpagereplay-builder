```
docker build -t soulgalore/webpagereplaybuilder .
docker run -v "$(pwd)":/output soulgalore/webpagereplaybuilder
```


Change *_SUPPORTED_PLATFORMS* in **build.py** to build for other platforms.
