CXX=g++
CFLAGS=`pkg-config --cflags gtk+-2.0` -g
CXXFLAGS=`pkg-config --cflags gtk+-2.0` -g
LDFLAGS=`pkg-config --libs gtk+-2.0`

%.exe: %.o
	$(CXX) $< -o $@ $(CFLAGS) $(LDFLAGS)

all: main.exe

clean:
	rm -f *.o *.exe *.dll
