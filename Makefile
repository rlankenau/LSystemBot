.PHONY: dep run

dep:
	brew install python
	pip3 install -r requirements.txt

run:
	python3 lsysbot.py
