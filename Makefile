all: python-zpar

clean:
	rm -rf /tmp/zpar
	rm -f /tmp/zpar.tar.gz

python-zpar: clean /tmp/zpar.tar.gz
	tar -C /tmp/zpar -zxf /tmp/zpar.tar.gz --strip-components=1
	cp src/zpar.lib.cpp /tmp/zpar/src/english
	cp src/Makefile.lib.zpar /tmp/zpar
	cp src/Makefile /tmp/zpar
	cp src/reader.h /tmp/zpar/src/include/reader.h
	make -C /tmp/zpar zpar.so
	mkdir -p zpar/dist
	cp /tmp/zpar/dist/zpar.so zpar/dist/

/tmp/zpar.tar.gz:
	wget -N http://sourceforge.net/projects/zpar/files/latest/zpar.tar.gz -O /tmp/zpar.tar.gz
	touch $@
	mkdir /tmp/zpar

