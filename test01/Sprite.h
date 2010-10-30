#include <gtk/gtk.h>

class Sprite
{
protected:
    double x, y, width, height;
public:
    Sprite(double x, double y, double width, double height);
    ~Sprite();
    virtual void do_tick(unsigned long tick) = 0;
    virtual void do_draw(cairo_t *cr) = 0;
};
