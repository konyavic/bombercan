CC=g++
CFLAGS=`pkg-config --cflags gtk+-2.0`
LDFLAGS=`pkg-config --libs gtk+-2.0`

test01.exe: test01.o
	$(CC) $< -o $@ $(CFLAGS) $(LDFLAGS)

all: test01.exe

clean:
	rm -f *.o *.exe
