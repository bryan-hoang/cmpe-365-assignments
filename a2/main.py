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

windowWidth = 1000  # window dimensions
windowHeight = 1000

minX = None  # range of vertices
maxX = None
minY = None
maxY = None

r = 0.008  # point radius as fraction of window size

allVerts: list[list[float]] = []  # all triangle vertices

lastKey = None  # last key pressed

showForwardLinks = True


class Triangle(object):
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
        self.adjTris: list[Triangle] = []  # adjacent triangles

        self.nextTri: Triangle | None = None  # next triangle on strip
        self.prevTri: Triangle | None = None  # previous triangle on strip

        self.highlight1 = (
            False  # to cause drawing to highlight this triangle in colour 1
        )
        self.highlight2 = (
            False  # to cause drawing to highlight this triangle in colour 2
        )

        self.centroid = (
            sum([allVerts[i][0] for i in self.verts]) / len(self.verts),
            sum([allVerts[i][1] for i in self.verts]) / len(self.verts),
        )

        self.id = Triangle.nextID
        Triangle.nextID += 1

    def __repr__(self):
        """Represent this triangle as a string."""
        return "tri-%d" % self.id

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

    def drawPointers(self):
        """Draw edges to next and previous triangle on the strip."""
        if showForwardLinks and self.nextTri:
            glColor3f(0, 0, 1)
            drawArrow(
                self.centroid[0],
                self.centroid[1],
                self.nextTri.centroid[0],
                self.nextTri.centroid[1],
            )

        if not showForwardLinks and self.prevTri:
            glColor3f(1, 0, 0)
            drawArrow(
                self.centroid[0],
                self.centroid[1],
                self.prevTri.centroid[0],
                self.prevTri.centroid[1],
            )

        if not self.nextTri and not self.prevTri:  # no links.  Draw a dot.
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

    def containsPoint(self, pt):
        """Determine whether this triangle contains a point."""
        return (
            turn(allVerts[self.verts[0]], allVerts[self.verts[1]], pt)
            == LEFT_TURN
            and turn(allVerts[self.verts[1]], allVerts[self.verts[2]], pt)
            == LEFT_TURN
            and turn(allVerts[self.verts[2]], allVerts[self.verts[0]], pt)
            == LEFT_TURN
        )


def drawArrow(x0, y0, x1, y1):
    """Draw an arrow between two points."""
    d = math.sqrt((x1 - x0) * (x1 - x0) + (y1 - y0) * (y1 - y0))

    vx = (x1 - x0) / d  # unit direction (x0,y0) -> (x1,y1)
    vy = (y1 - y0) / d

    vpx = -vy  # unit direction perpendicular to (vx,vy)
    vpy = vx

    xa = x0 + 0.15 * r * vx  # arrow tail
    ya = y0 + 0.15 * r * vy

    xb = x1 - 0.15 * r * vx  # arrow head
    yb = y1 - 0.15 * r * vy

    xc = xb - 2 * r * vx + 0.5 * r * vpx  # arrow outside left
    yc = yb - 2 * r * vy + 0.5 * r * vpy

    xd = xb - 2 * r * vx - 0.5 * r * vpx  # arrow outside right
    yd = yb - 2 * r * vy - 0.5 * r * vpy

    glBegin(GL_LINES)
    glVertex2f(xa, ya)
    glVertex2f(0.5 * (xc + xd), 0.5 * (yc + yd))
    glEnd()

    glBegin(GL_LINE_LOOP)
    glVertex2f(xb, yb)
    glVertex2f(xc, yc)
    glVertex2f(xd, yd)
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


def buildTristrips(triangles: list[Triangle]):
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
                int(not adjacent_triangle.nextTri)
                for adjacent_triangle in triangle.adjTris
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
            *current_strip_triangle.adjTris
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

            current_strip_triangle.nextTri = next_strip_triangle
            next_strip_triangle.prevTri = current_strip_triangle

            # Continue building the triangle strip.
            current_strip_triangle = next_strip_triangle
            adj_non_strip_triangles = {
                *current_strip_triangle.adjTris
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

    for tri in allTriangles:
        tri.draw()

    # Draw pointers.  Do this *after* the triangles (above) so that the
    # triangle drawing doesn't overlay the pointers.

    for tri in allTriangles:
        tri.drawPointers()

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


def keyCallback(_window, key, _scancode, action, _mods):
    """Handle keyboard input."""
    global lastKey, showForwardLinks

    if action == glfw.RELEASE:
        if key == glfw.KEY_ESCAPE:  # quit upon ESC
            sys.exit(0)
        elif key == ord("F"):  # toggle forward/backward link display
            showForwardLinks = not showForwardLinks
        else:
            lastKey = key


def windowReshapeCallback(_window, newWidth, newHeight):
    """Handle window reshape."""
    global windowWidth, windowHeight

    windowWidth = newWidth
    windowHeight = newHeight


def mouseButtonCallback(window, _btn, action, _keyModifiers):
    """Handle mouse click/release."""
    if action == glfw.PRESS:

        # Find point under mouse

        x, y = glfw.get_cursor_pos(window)  # mouse position

        wx = (x - 0) / float(windowWidth) * (
            windowRight - windowLeft
        ) + windowLeft
        wy = (windowHeight - y) / float(windowHeight) * (
            windowTop - windowBottom
        ) + windowBottom

        selectedTri = None
        for tri in allTriangles:
            if tri.containsPoint([wx, wy]):
                selectedTri = tri
                break

        # Print triangle, toggle its highlight1, and toggle the highlight2s of
        # its adjacent triangles.

        if selectedTri:
            selectedTri.highlight1 = not selectedTri.highlight1
            print(
                "%s with adjacent %s"
                % (selectedTri, repr(selectedTri.adjTris))
            )
            for t in selectedTri.adjTris:
                t.highlight2 = not t.highlight2


def readTriangles(f):
    """Read triangles from a file."""
    global allVerts

    errorsFound = False

    lines = f.readlines()

    # Read the vertices

    numVerts = int(lines[0])
    allVerts = [
        [float(c) for c in line.split()] for line in lines[1 : numVerts + 1]
    ]

    # Check that the vertices are valid

    for line_number, v in enumerate(allVerts):
        if len(v) != 2:
            print(
                "Line %d: vertex does not have two coordinates."
                % (line_number + 2)
            )
            errorsFound = True

    # Read the triangles

    numTris = int(lines[numVerts + 1])
    triVerts = [
        [int(v) for v in line.split()] for line in lines[numVerts + 2 :]
    ]

    # Check that the triangle vertices are valid

    for line_number, tvs in enumerate(triVerts):
        if len(tvs) != 3:
            print(
                "Line %d: triangle does not have three vertices."
                % (line_number + 2 + numVerts)
            )
            errorsFound = True
        else:
            for v in tvs:
                if v < 0 or v >= numVerts:
                    print(
                        "Line %d: Vertex index is not in range [0,%d]."
                        % (line_number + 2 + numVerts, numVerts - 1)
                    )
                    errorsFound = True

    # Build triangles

    tris: list[Triangle] = []

    for tvs in triVerts:
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
            adjTris = []
            for i in range(3):
                v0 = tri.verts[i % 3]
                v1 = tri.verts[(i + 1) % 3]
                for tri2 in tris:
                    for j in range(3):
                        if (
                            v1 == tri2.verts[j % 3]
                            and v0 == tri2.verts[(j + 1) % 3]
                        ):
                            adjTris.append(tri2)
                    if len(adjTris) == 3:
                        break
            tri.adjTris = adjTris

    else:  # hashing

        edges = {}

        for tri in tris:
            for i in range(3):
                v0 = tri.verts[i % 3]
                v1 = tri.verts[(i + 1) % 3]
                key = "%f-%f" % (v0, v1)
                edges[key] = tri

        for tri in tris:
            adjTris = []
            for i in range(3):
                v1 = tri.verts[
                    i % 3
                ]  # find a reversed edge of an adjacent triangle
                v0 = tri.verts[(i + 1) % 3]
                key = "%f-%f" % (v0, v1)
                if key in edges:
                    adjTris.append(edges[key])
                if len(adjTris) == 3:
                    break
            tri.adjTris = adjTris

    print("Read %d points and %d triangles" % (numVerts, numTris))

    if errorsFound:
        return []
    else:
        return tris


def main():
    """Initialize GLFW and run the main event loop."""
    global window, allTriangles, minX, maxX, minY, maxY, r

    # Check command-line args

    if len(sys.argv) < 2:
        print("Usage: %s filename" % sys.argv[0])
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
        windowWidth, windowHeight, "Assignment 2", None, None
    )

    if not window:
        glfw.terminate()
        print("Error: GLFW failed to create a window")
        sys.exit(1)

    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_key_callback(window, keyCallback)
    glfw.set_window_size_callback(window, windowReshapeCallback)
    glfw.set_mouse_button_callback(window, mouseButtonCallback)

    # Read the triangles.  This also fills in the global 'allVerts'.

    with open(args[0], "rb") as f:
        allTriangles = readTriangles(f)

    if allTriangles == []:
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

    buildTristrips(allTriangles)

    # Show result and wait to exit

    display(wait=True)

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
