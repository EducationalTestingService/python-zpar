all: python-zpar

clean:
	rm -rf /tmp/zpar

python-zpar: clean zpar.zip
	unzip -q /tmp/zpar.zip -d /tmp
	cp src/zpar.lib.cpp /tmp/zpar/src/english
	cp src/Makefile.lib.zpar /tmp/zpar
	cp src/Makefile /tmp/zpar
	cp src/reader.h /tmp/zpar/src/include/reader.h
	make -C /tmp/zpar zpar.so
	mkdir -p dist
	cp /tmp/zpar/dist/zpar.so dist/

zpar.zip:
	wget -N http://sourceforge.net/projects/zpar/files/latest/zpar.zip -O /tmp/zpar.zip
	touch $@

