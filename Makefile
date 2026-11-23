.PHONY: all render preview clean help

all: render

render:
	quarto render
	@touch docs/.nojekyll

preview:
	quarto preview

clean:
	rm -rf docs .quarto

help:
	@echo "  make          render the site to docs/"
	@echo "  make preview  live-reload preview server"
	@echo "  make clean    remove docs/ and .quarto/"
