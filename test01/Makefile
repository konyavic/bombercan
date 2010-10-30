CC=g++
CFLAGS=`pkg-config --cflags gtk+-2.0`
LDFLAGS=`pkg-config --libs gtk+-2.0`

%.exe: %.o
	$(CC) $< -o $@ $(CFLAGS) $(LDFLAGS)

all: main.exe

clean:
	rm -f *.o *.exe
