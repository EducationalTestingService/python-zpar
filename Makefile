all: python-zpar

clean:
	rm -rf /tmp/zpar
	rm -f /tmp/zpar.zip

python-zpar: clean /tmp/zpar.zip
	unzip -q /tmp/zpar.zip -d /tmp
	cp src/zpar.lib.cpp /tmp/zpar/src/english
	cp src/Makefile.lib.zpar /tmp/zpar
	cp src/Makefile /tmp/zpar
	cp src/reader.h /tmp/zpar/src/include/reader.h
	make -C /tmp/zpar zpar.so
	mkdir -p zpar/dist
	cp /tmp/zpar/dist/zpar.so zpar/dist/

/tmp/zpar.zip:
	wget -N http://sourceforge.net/projects/zpar/files/latest/zpar.zip -O /tmp/zpar.zip
	touch $@

