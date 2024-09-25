PYTHONPATH := $(shell pwd)

install:
	pip install --upgrade pip && pip install -r requirements.txt

run:
	@export PYTHONPATH=$(PYTHONPATH) &&\
		python3 etl/footwear/hangar.py