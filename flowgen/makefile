all: convert flowgen

convert: 
	gcc ./src/convert.c -o ./bin/convert

flowgen:
	gcc ./src/flowgen.c -o ./bin/flowgen

clean: 
	rm -rf bin/convert bin/flowgen