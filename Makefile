all:
	@echo "Nothing to do for all"

clean:
	make -C tests/ clean
	rm -f *.pyc lib/*.pyc flask/*.pyc
	rm -rf __pycache__ lib/__pycache__ flask/__pycache__

tests:
	make -C tests/

.PHONY: tests
