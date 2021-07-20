#escape=`
FROM rackspacedot/python37:latest

ENV RADARR_HOST_URL=http://localhost:7878
ENV RADARR_API_KEY=00000000000000000000000000000000
ENV COUNTRY=PL
ENV SCAN_INTERVAL=43200

WORKDIR /radarr_justwatch
COPY radarr_justwatch.py requirements.txt run.sh ./

RUN python3 -m pip install -r requirements.txt
RUN chmod +x radarr_justwatch.py run.sh

ENTRYPOINT ./run.sh