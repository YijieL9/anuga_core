"""
This is the first prototype (testing) for the ANUGA & SWMM coupling project

In this testing, we are expecting to create a one-pipe testing. Flowing water out from ANUGA to SWMM, and using the SWMM
calculate the water flow activities in the pipe, and flows back to ANUGA.

we can validate this testing by monitor the change of the water total volume. It should remains the same between flowing
to SWMM and flowing back to ANUGA.
"""

# ------------------------------------------------------------------------------
# Import necessary modules
# ------------------------------------------------------------------------------
from anuga import rectangular_cross
from anuga import Domain
from anuga import Reflective_boundary
from anuga import Dirichlet_boundary
from anuga.operators.rate_operators import Rate_operator
from anuga import Time_boundary

# ------------------------------------------------------------------------------
# Setup computational domain
# ------------------------------------------------------------------------------
length = 15.
width = 5.
dx = dy = 0.5  # .1           # Resolution: Length of subdivisions on both axes

points, vertices, boundary = rectangular_cross(int(length / dx), int(width / dy),
                                               len1=length, len2=width)
domain = Domain(points, vertices, boundary)
domain.set_name('total_volume_testing')  # Output name based on script name. You can add timestamp=True
print(domain.statistics())


# ------------------------------------------------------------------------------
# Setup initial conditions
# ------------------------------------------------------------------------------
def topography(x, y):
    """Complex topography defined by a function of vectors x and y."""

    z = 0 * x - 5

    # higher pools
    id = x < 5
    z[id] = -3

    # wall
    id = (5 < x) & (x < 10)
    z[id] = 0

    # inflow pipe hole, located at (2, 2), r = 0.3, depth 0.1
    id = (x - 2) ** 2 + (y - 2) ** 2 < 0.3 ** 2
    z[id] -= 0.2

    # inflow pipe hole, located at (12, 2), r = 0.3, depth 0.1
    id = (x - 12) ** 2 + (y - 2) ** 2 < 0.3 ** 2
    z[id] -= 0.2

    return z


# ------------------------------------------------------------------------------
# Setup initial quantity
# ------------------------------------------------------------------------------
domain.set_quantity('elevation', topography)  # elevation is a function
domain.set_quantity('friction', 0.01)  # Constant friction
domain.set_quantity('stage', expression='elevation')  # Dry initial condition

# ------------------------------------------------------------------------------
# Setup boundaries
# ------------------------------------------------------------------------------
Bi = Dirichlet_boundary([0.1, 0, 0])  # Inflow
Br = Reflective_boundary(domain)  # Solid reflective wall
Bo = Dirichlet_boundary([-5, 0, 0])  # Outflow

domain.set_boundary({'left': Br, 'right': Br, 'top': Br, 'bottom': Br})

# ------------------------------------------------------------------------------
# Setup inject water
# ------------------------------------------------------------------------------
inject_op = Rate_operator(domain, radius=0.5, center=(2.5, 2.5))
outflow_op = Rate_operator(domain, radius=0.3, center=(2., 2.)) #
inflow_op = Rate_operator(domain, radius=0.3, center=(12., 2)) #


def inject_water(t): # inject water volume will change by time
    if t > 2:
        return 0
    else:
        return 10


for t in domain.evolve(yieldstep=0.5, finaltime=15.0):
    inject_op.set_rate(inject_water(t))
    domain.print_timestepping_statistics()
