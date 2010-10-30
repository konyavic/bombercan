#include <gtk/gtk.h>
#include <math.h>
#include "Sprite.h"

#define INC_CIRCULAR(C, D, MAX, MIN)    \
    C = C+D;                            \
    if (C>MAX || C<MIN)                 \
        D = -D;

cairo_surface_t *sprite_surface;

void draw_sprite(cairo_surface_t *surface)
{
    
}

class MySprite: public Sprite
{
protected:
    double alpha, d_alpha;
    double sw, d_sw, sh, d_sh;
public:
    MySprite(double x, double y, double w, double h):
        Sprite(x, y, w, h), 
        alpha(0), d_alpha(0.02),
        sw(1), d_sw(0.05), sh(0.5), d_sh(0.05)
    {};
    void do_tick(unsigned long int) 
    {
        INC_CIRCULAR(alpha, d_alpha, 1, 0);
        INC_CIRCULAR(sw, d_sw, 2, 0.5);
        INC_CIRCULAR(sh, d_sh, 2, 0.5);
    };
    void do_draw(cairo_t *target_cr)
    {
        cairo_t *cr;

        cairo_surface_t *surface = cairo_image_surface_create(
            CAIRO_FORMAT_ARGB32, width, height);
        cr = cairo_create(surface);

        cairo_scale (cr, sw, sh);

        cairo_set_source_rgba(cr, 0, 0, 1, 0.5);
        cairo_rectangle(cr, 0, 0, 60, 60);
        cairo_fill(cr);

        cairo_set_source_rgba(cr, 0, 1, 0, 0.5);
        cairo_rectangle(cr, 30, 30, 60, 60);
        cairo_fill(cr);

        cairo_destroy(cr);

        cairo_pattern_t *sprite_mask = cairo_pattern_create_rgba(0, 0, 0, alpha);
        cairo_set_source_surface(target_cr, surface, x, y);
        cairo_mask(target_cr, sprite_mask);

        cairo_surface_destroy(surface);
    };
};

MySprite *s;

void draw(GtkWidget *widget, cairo_t *cr)
{
    double dx, dy;
    double radius;
    cairo_pattern_t *linpat, *radpat;
    static double c1=0, c2=1, c3=0.3, c4=0.8;
    static double cd1 = 0.01, cd2 = 0.02, cd3 = 0.03, cd4 = 0.04;
    static double move=0, dmove=1.2;

    dx = widget->allocation.x + widget->allocation.width;
    dy = widget->allocation.y + widget->allocation.height;
    radius = MIN(widget->allocation.width / 2,
            widget->allocation.height / 2) - 5;

    linpat = cairo_pattern_create_linear(0, 0, dx, dy);
    cairo_pattern_add_color_stop_rgb(linpat, 0, c1, c3, c4);
    cairo_pattern_add_color_stop_rgb(linpat, 0.25, c1, c3, c4);
    cairo_pattern_add_color_stop_rgb(linpat, 0.5, c2, c3, c4);
    cairo_pattern_add_color_stop_rgb(linpat, 0.75, c1, c4, c3);
    cairo_pattern_add_color_stop_rgb(linpat, 1, c1, c4, c3);
    radpat = cairo_pattern_create_radial(dx/2, dy/2, radius*0.5, dx/2, dy/2, radius);
    cairo_pattern_add_color_stop_rgba(radpat, 0, 0, 0, 0, 1);
    cairo_pattern_add_color_stop_rgba(radpat, 1, 0, 0, 0, 0);

    cairo_set_source(cr, linpat);
    cairo_mask(cr, radpat);

    cairo_arc(cr, dx/2+move, dy/2, radius/2, 0, 2 * M_PI);
    cairo_set_source_rgba(cr, c4, c4, c3, 0.3);
    cairo_fill_preserve(cr);

    double w = move > 0 ? move : -move;
    cairo_set_source_rgba(cr, 0, 0, 0, 0.3);
    cairo_set_line_width(cr, w/5);
    cairo_stroke(cr);

    INC_CIRCULAR(c1, cd1, 1, 0);
    INC_CIRCULAR(c2, cd2, 1, 0);
    INC_CIRCULAR(c3, cd3, 1, 0);
    INC_CIRCULAR(c4, cd4, 1, 0);
    INC_CIRCULAR(move, dmove, 50, -50);

    s->do_tick(0);
    s->do_draw(cr);
}

gboolean area_expose_event(GtkWidget *widget, 
        GdkEvent *_event, 
        gpointer userdata)
{
    cairo_t *cr;
    GdkEventExpose *event = (GdkEventExpose *) _event;

    cr = gdk_cairo_create(widget->window);

    cairo_rectangle(cr, event->area.x, event->area.y, event->area.width, event->area.height);
    cairo_clip(cr);

    draw(widget, cr);

    cairo_destroy(cr);

    return FALSE;
}

gboolean time_handler(GtkWidget *widget)
{
    gtk_widget_queue_draw(widget);
    return TRUE;
}

int main(int argc, char *argv[])
{
    GtkWidget *window;
    GtkWidget *area;
    GtkWidget *fixed;

    gtk_init(&argc, &argv);

    window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    area = gtk_drawing_area_new();

    s = new MySprite(200, 200, 200, 200);

    g_signal_connect(area, "expose-event", G_CALLBACK(area_expose_event), NULL);
    g_timeout_add(1000/60, (GSourceFunc) time_handler, (gpointer) area);

    gtk_window_set_title((GtkWindow *) window, "cairo skeleten");
    gtk_widget_set_size_request(area, 640, 480);

    gtk_container_add(GTK_CONTAINER(window), area);

    gtk_widget_show_all(window);

    gtk_main();

    return 0;
}

