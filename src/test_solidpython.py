from solid import *
from solid.utils import *  # Hilfsfunktionen (z.B. `up()`, `right()`)

cube = cube([10, 20, 5])
cylinder = translate([15, 0, 0])(cylinder(r=3, h=10))

# Kombiniere Objekte
model = union()(cube, cylinder)

# Exportiere nach .scad
scad_render_to_file(model, "mechanism.scad")