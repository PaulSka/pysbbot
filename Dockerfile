from hypriot/rpi-python
MAINTAINER LYSAKOWSKIM Mathieu (lysakowskimg@gmail.com)
ENV PYTHONUNBUFFERED=0
RUN apt-get update -y
RUN apt-get install libxml2 libxslt -y
RUN pip-2.7 install requests beautifulsoup4 socketIO-client lxml