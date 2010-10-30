#include <gtk/gtk.h>
#include "Sprite.h"

Sprite::Sprite(double x, double y, double width, double height)
{
    this->x = x;
    this->y = y;
    this->width = width;
    this->height = height;
}

Sprite::~Sprite()
{
}
