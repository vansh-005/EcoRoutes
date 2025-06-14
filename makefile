.PHONY: osrm-build osrm-up

CITY        ?= northern-zone-latest
PROFILE     ?= car
PBF         := data/$(CITY).osm.pbf

osrm-build:
	docker run --rm -v ${PWD}/data:/data osrm/osrm-backend osrm-extract -p /opt/$(PROFILE).lua /data/$(CITY).osm.pbf
	docker run --rm -v ${PWD}/data:/data osrm/osrm-backend osrm-contract /data/$(CITY).osm.pbf.osrm

osrm-up: osrm-build
	docker compose -f docker-compose.osrm.yml up -d
