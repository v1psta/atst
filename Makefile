test:
	python -m pytest

clean:
	find static/assets -type f |grep -v .gitignore | xargs rm
