.PHONY: site gulp build render

site: gulp build render

gulp:
	python3 pipeline/01_gulp_data.py

build:
	python3 pipeline/02_build_listings.py

render:
	quarto render
