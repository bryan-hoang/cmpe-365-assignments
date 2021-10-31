"""
Triangle strips.

Usage: python main.py file_of_triangles

You can press ESC in the window to exit.

You'll need Python 3 and must install these packages:

  PyOpenGL, GLFW
"""

import math
import sys

try:  # PyOpenGL
    from OpenGL.GL import (
        GL_COLOR_BUFFER_BIT,
        GL_FILL,
        GL_FRONT_AND_BACK,
        GL_LINE_LOOP,
        GL_LINES,
        GL_MODELVIEW,
        GL_POLYGON,
        GL_PROJECTION,
        glBegin,
        glClear,
        glClearColor,
        glColor3f,
        glEnd,
        glLoadIdentity,
        glMatrixMode,
        glOrtho,
        glPolygonMode,
        glVertex2f,
    )
except ModuleNotFoundError:
    print("Error: PyOpenGL has not been installed.")
    sys.exit(0)

try:  # GLFW
    import glfw
except ModuleNotFoundError:
    print("Error: GLFW has not been installed.")
    sys.exit(0)


# Globals

window = None

window_width = 1000  # window dimensions
window_height = 1000

minX = None  # range of vertices
maxX = None
minY = None
maxY = None

r = 0.008  # point radius as fraction of window size

allVerts: list[list[float]] = []  # all triangle vertices

lastKey = None  # last key pressed

showForwardLinks = True


class Triangle:
    """A Triangle stores its three vertices and pointers to any adjacent triangles.

    For debugging, you can set the 'highlight1' and 'highlight2' flags
    of a triangle.  This will cause the triangle to be highlighted when
    it's drawn.
    """

    nextID = 0

    def __init__(self, verts: list[int]):
        """Initialize a triangle with the given vertices."""
        self.verts = (
            verts  # 3 vertices.  Each is an index into the 'allVerts' global.
        )
        self.adj_tris: list[Triangle] = []  # adjacent triangles

        self.next_tri: Triangle | None = None  # next triangle on strip
        self.prev_tri: Triangle | None = None  # previous triangle on strip

        self.highlight1 = (
            False  # to cause drawing to highlight this triangle in colour 1
        )
        self.highlight2 = (
            False  # to cause drawing to highlight this triangle in colour 2
        )

        self.centroid = (
            sum(allVerts[i][0] for i in self.verts) / len(self.verts),
            sum(allVerts[i][1] for i in self.verts) / len(self.verts),
        )

        self.id = Triangle.nextID
        Triangle.nextID += 1

    def __repr__(self):
        """Represent this triangle as a string."""
        return f"tri-{self.id:d}"

    def draw(self):
        """Draw this triangle."""
        # Highlight with yellow fill
        if self.highlight1 or self.highlight2:

            if self.highlight1:
                glColor3f(0.9, 0.9, 0.4)  # dark yellow
            else:
                glColor3f(1, 1, 0.8)  # light yellow

            glBegin(GL_POLYGON)
            for i in self.verts:
                glVertex2f(allVerts[i][0], allVerts[i][1])
            glEnd()

        # Outline the triangle

        glColor3f(0, 0, 0)
        glBegin(GL_LINE_LOOP)
        for i in self.verts:
            glVertex2f(allVerts[i][0], allVerts[i][1])
        glEnd()

    def draw_pointers(self):
        """Draw edges to next and previous triangle on the strip."""
        if showForwardLinks and self.next_tri:
            glColor3f(0, 0, 1)
            draw_arrow(
                self.centroid[0],
                self.centroid[1],
                self.next_tri.centroid[0],
                self.next_tri.centroid[1],
            )

        if not showForwardLinks and self.prev_tri:
            glColor3f(1, 0, 0)
            draw_arrow(
                self.centroid[0],
                self.centroid[1],
                self.prev_tri.centroid[0],
                self.prev_tri.centroid[1],
            )

        if not self.next_tri and not self.prev_tri:  # no links.  Draw a dot.
            if showForwardLinks:
                glColor3f(0, 0, 1)
            else:
                glColor3f(1, 0, 0)
            glBegin(GL_POLYGON)
            for i in range(100):
                theta = 3.14159 * i / 50.0
                glVertex2f(
                    self.centroid[0] + 0.5 * r * math.cos(theta),
                    self.centroid[1] + 0.5 * r * math.sin(theta),
                )
            glEnd()

    def contains_point(self, point):
        """Determine whether this triangle contains a point."""
        return (
            turn(allVerts[self.verts[0]], allVerts[self.verts[1]], point)
            == LEFT_TURN
            and turn(allVerts[self.verts[1]], allVerts[self.verts[2]], point)
            == LEFT_TURN
            and turn(allVerts[self.verts[2]], allVerts[self.verts[0]], point)
            == LEFT_TURN
        )


all_triangles: list[Triangle] = []


def draw_arrow(x_0, y_0, x_1, y_1):
    """Draw an arrow between two points."""
    distance = math.sqrt((x_1 - x_0) * (x_1 - x_0) + (y_1 - y_0) * (y_1 - y_0))

    v_x = (x_1 - x_0) / distance  # unit direction (x0,y0) -> (x1,y1)
    v_y = (y_1 - y_0) / distance

    vpx = -v_y  # unit direction perpendicular to (vx,vy)
    vpy = v_x

    x_a = x_0 + 0.15 * r * v_x  # arrow tail
    y_a = y_0 + 0.15 * r * v_y

    x_b = x_1 - 0.15 * r * v_x  # arrow head
    y_b = y_1 - 0.15 * r * v_y

    x_c = x_b - 2 * r * v_x + 0.5 * r * vpx  # arrow outside left
    y_c = y_b - 2 * r * v_y + 0.5 * r * vpy

    x_d = x_b - 2 * r * v_x - 0.5 * r * vpx  # arrow outside right
    y_d = y_b - 2 * r * v_y - 0.5 * r * vpy

    glBegin(GL_LINES)
    glVertex2f(x_a, y_a)
    glVertex2f(0.5 * (x_c + x_d), 0.5 * (y_c + y_d))
    glEnd()

    glBegin(GL_LINE_LOOP)
    glVertex2f(x_b, y_b)
    glVertex2f(x_c, y_c)
    glVertex2f(x_d, y_d)
    glEnd()


LEFT_TURN = 1
RIGHT_TURN = 2
COLLINEAR = 3


def turn(a, b, c):
    """Determine whether three points make a left or right turn."""
    det = (a[0] - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (a[1] - c[1])

    if det > 0:
        return LEFT_TURN
    elif det < 0:
        return RIGHT_TURN
    else:
        return COLLINEAR


# ================================================================
# ================================================================
# ================================================================


def build_tristrips(triangles: list[Triangle]):
    """
    Build a set of triangle strips that cover all of the given triangles.

    The goal is to make the strips as long as possible
    (i.e., to have the fewest strip that cover all triangles).

    Follow the instructions in A2.txt.

    This function does not return anything.  The strips are formed by
    modifying the 'nextTri' and 'prevTri' pointers in each triangle.
    """
    # Common logic for selecting a triangle with a minimum number of adjacent
    # non-strip triangles.
    def get_triangle_with_min_adj_non_strip_triangles(
        triangles: set[Triangle],
    ):
        def count_adj_non_strip_triangles(triangle: Triangle):
            return sum(
                # If `nextTri` isn't set, `prevTri` isn't set either.
                int(not adjacent_triangle.next_tri)
                for adjacent_triangle in triangle.adj_tris
            )

        return min(triangles, key=count_adj_non_strip_triangles)

    # Converting to a set to get access to set removal and intersection. Also,
    # the ordering of a list isn't used.
    non_strip_triangles: set[Triangle] = {*triangles}
    triangle_strip_count: int = 0

    # Begin building the triangle strips.
    while non_strip_triangles:
        # Start a new triangle strip
        triangle_strip_count += 1
        current_strip_triangle: Triangle = (
            get_triangle_with_min_adj_non_strip_triangles(non_strip_triangles)
        )
        non_strip_triangles -= {current_strip_triangle}

        # Get eligible triangles to add to the strip.
        adj_non_strip_triangles: set[Triangle] = {
            *current_strip_triangle.adj_tris
        } & non_strip_triangles

        # Build the triangle strip.
        while adj_non_strip_triangles:
            # Add another triangle to the strip.
            next_strip_triangle: Triangle = (
                get_triangle_with_min_adj_non_strip_triangles(
                    adj_non_strip_triangles
                )
            )
            non_strip_triangles -= {next_strip_triangle}

            current_strip_triangle.next_tri = next_strip_triangle
            next_strip_triangle.prev_tri = current_strip_triangle

            # Continue building the triangle strip.
            current_strip_triangle = next_strip_triangle
            adj_non_strip_triangles = {
                *current_strip_triangle.adj_tris
            } & non_strip_triangles

    print(f"Generated {triangle_strip_count} tristrips")


# ================================================================
# ================================================================
# ================================================================


windowLeft = None
windowRight = None
windowTop = None
windowBottom = None


def display(wait=False):
    """Set up the display and draw the current image."""
    global lastKey, windowLeft, windowRight, windowBottom, windowTop

    # Handle any events that have occurred

    glfw.poll_events()

    # Set up window

    glClearColor(1, 1, 1, 0)
    glClear(GL_COLOR_BUFFER_BIT)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if maxX - minX > maxY - minY:  # wider point spread in x direction
        windowLeft = -0.1 * (maxX - minX) + minX
        windowRight = 1.1 * (maxX - minX) + minX
        windowBottom = windowLeft
        windowTop = windowRight
    else:  # wider point spread in y direction
        windowTop = -0.1 * (maxY - minY) + minY
        windowBottom = 1.1 * (maxY - minY) + minY
        windowLeft = windowBottom
        windowRight = windowTop

    glOrtho(windowLeft, windowRight, windowBottom, windowTop, 0, 1)

    # Draw triangles

    for tri in all_triangles:
        tri.draw()

    # Draw pointers.  Do this *after* the triangles (above) so that the
    # triangle drawing doesn't overlay the pointers.

    for tri in all_triangles:
        tri.draw_pointers()

    # Show window

    glfw.swap_buffers(window)

    # Maybe wait until the user presses 'p' to proceed

    if wait:
        sys.stderr.write('Press "p" to proceed ')
        sys.stderr.flush()

        lastKey = None
        while lastKey != 80:  # wait for 'p'
            glfw.wait_events()
            display()

        sys.stderr.write("\r                     \r")
        sys.stderr.flush()


def key_callback(_window, key, _scancode, action, _mods):
    """Handle keyboard input."""
    global lastKey, showForwardLinks

    if action == glfw.RELEASE:
        if key == glfw.KEY_ESCAPE:  # quit upon ESC
            sys.exit(0)
        elif key == ord("F"):  # toggle forward/backward link display
            showForwardLinks = not showForwardLinks
        else:
            lastKey = key


def window_reshape_callback(_window, new_width, new_height):
    """Handle window reshape."""
    global window_width, window_height

    window_width = new_width
    window_height = new_height


def mouse_button_callback(window, _btn, action, _key_modifiers):
    """Handle mouse click/release."""
    if action == glfw.PRESS:

        # Find point under mouse

        x, y = glfw.get_cursor_pos(window)  # mouse position

        w_x = (x - 0) / float(window_width) * (
            windowRight - windowLeft
        ) + windowLeft
        w_y = (window_height - y) / float(window_height) * (
            windowTop - windowBottom
        ) + windowBottom

        selected_tri: Triangle = None
        for tri in all_triangles:
            if tri.contains_point([w_x, w_y]):
                selected_tri = tri
                break

        # Print triangle, toggle its highlight1, and toggle the highlight2s of
        # its adjacent triangles.

        if selected_tri:
            selected_tri.highlight1 = not selected_tri.highlight1
            print(
                f"{selected_tri} with adjacent {repr(selected_tri.adj_tris)}"
            )
            for adjacent_triangle in selected_tri.adj_tris:
                adjacent_triangle.highlight2 = not adjacent_triangle.highlight2


def read_triangles(file):
    """Read triangles from a file."""
    global allVerts

    errors_found = False

    lines = file.readlines()

    # Read the vertices

    num_verts = int(lines[0])
    allVerts = [
        [float(c) for c in line.split()] for line in lines[1 : num_verts + 1]
    ]

    # Check that the vertices are valid

    for line_number, vertex in enumerate(allVerts):
        if len(vertex) != 2:
            print(
                f"Line {line_number + 2}: "
                f"vertex does not have two coordinates."
            )
            errors_found = True

    # Read the triangles

    num_tris = int(lines[num_verts + 1])
    tri_verts = [
        [int(v) for v in line.split()] for line in lines[num_verts + 2 :]
    ]

    # Check that the triangle vertices are valid

    for line_number, tvs in enumerate(tri_verts):
        if len(tvs) != 3:
            print(
                f"Line {line_number + 2 + num_verts}:"
                f" triangle does not have three vertices."
            )
            errors_found = True
        else:
            for vertex in tvs:
                if vertex < 0 or vertex >= num_verts:
                    print(
                        f"Line {line_number + 2 + num_verts}: "
                        f"Vertex index is not in range [0,{num_verts - 1}]."
                    )
                    errors_found = True

    # Build triangles

    tris: list[Triangle] = []

    for tvs in tri_verts:
        if (
            turn(allVerts[tvs[0]], allVerts[tvs[1]], allVerts[tvs[2]])
            != COLLINEAR
        ):
            tris.append(Triangle(tvs))  # (don't include degenerate triangles)

    # For each triangle, find and record its adjacent triangles
    #
    # This would normally take O(n^2) time if done by brute force, so
    # we'll exploit Python's hashed dictionary keys.

    if False:

        for tri in tris:  # brute force
            adj_tris = []
            for i in range(3):
                v_0 = tri.verts[i % 3]
                v_1 = tri.verts[(i + 1) % 3]
                for tri2 in tris:
                    for j in range(3):
                        if (
                            v_1 == tri2.verts[j % 3]
                            and v_0 == tri2.verts[(j + 1) % 3]
                        ):
                            adj_tris.append(tri2)
                    if len(adj_tris) == 3:
                        break
            tri.adj_tris = adj_tris

    else:  # hashing

        edges = {}

        for tri in tris:
            for i in range(3):
                v_0 = tri.verts[i % 3]
                v_1 = tri.verts[(i + 1) % 3]
                key = f"{v_0:f}-{v_1:f}"
                edges[key] = tri

        for tri in tris:
            adj_tris = []
            for i in range(3):
                v_1 = tri.verts[
                    i % 3
                ]  # find a reversed edge of an adjacent triangle
                v_0 = tri.verts[(i + 1) % 3]
                key = f"{v_0:f}-{v_1:f}"
                if key in edges:
                    adj_tris.append(edges[key])
                if len(adj_tris) == 3:
                    break
            tri.adj_tris = adj_tris

    print(f"Read {num_verts} points and {num_tris} triangles")

    if errors_found:
        return []
    else:
        return tris


def main():
    """Initialize GLFW and run the main event loop."""
    global window, all_triangles, minX, maxX, minY, maxY, r

    # Check command-line args

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} filename")
        sys.exit(1)

    args = sys.argv[1:]
    while len(args) > 1:
        # if args[0] == '-x':
        #     pass
        args = args[1:]

    # Set up window

    if not glfw.init():
        print("Error: GLFW failed to initialize")
        sys.exit(1)

    window = glfw.create_window(
        window_width, window_height, "Assignment 2", None, None
    )

    if not window:
        glfw.terminate()
        print("Error: GLFW failed to create a window")
        sys.exit(1)

    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_key_callback(window, key_callback)
    glfw.set_window_size_callback(window, window_reshape_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)

    # Read the triangles.  This also fills in the global 'allVerts'.

    with open(args[0], "rb") as file:
        all_triangles = read_triangles(file)

    if all_triangles == []:
        return

    # Get bounding box of points

    minX = min(p[0] for p in allVerts)
    maxX = max(p[0] for p in allVerts)
    minY = min(p[1] for p in allVerts)
    maxY = max(p[1] for p in allVerts)

    # Adjust point radius in proportion to bounding box

    if maxX - minX > maxY - minY:
        r *= maxX - minX
    else:
        r *= maxY - minY

    # Run the code

    build_tristrips(all_triangles)

    # Show result and wait to exit

    display(wait=True)

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
