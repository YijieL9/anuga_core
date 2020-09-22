"""Simple water flow example using ANUGA

Water flowing down a channel with a topography that varies with time
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
import os

# ------------------------------------------------------------------------------
# Setup computational domain
# ------------------------------------------------------------------------------
length = 24.
width = 5.
dx = dy = 0.5  # .1           # Resolution: Length of subdivisions on both axes

points, vertices, boundary = rectangular_cross(int(length / dx), int(width / dy),
                                               len1=length, len2=width)
domain = Domain(points, vertices, boundary)
domain.set_name('rate_operator_test')  # Output name based on script name. You can add timestamp=True
print(domain.statistics())


# ------------------------------------------------------------------------------
# Setup initial conditions
# ------------------------------------------------------------------------------
def topography(x, y):
    """Complex topography defined by a function of vectors x and y."""

    z = -x / 100

    # Step
    id = (2 < x) & (x < 4)
    z[id] += 0.4 - 0.05 * y[id]

    # Permanent pole
    id = (x - 8) ** 2 + (y - 2) ** 2 < 0.4 ** 2
    z[id] -= 0.2

    id = (x - 16) ** 2 + (y - 2) ** 2 < 0.4 ** 2
    z[id] -= 0.2

    # Dam
    # id = (12 < x) & (x  < 13)
    # z[id] += 0.4

    return z


def pole_increment(x, y, t):
    """This provides a small increment to a pole located mid stream
    For use with variable elevation data
    """

    z = 0.0 * x

    if t < 10.0:
        return z

    # Pole 1
    id = (x - 12) ** 2 + (y - 3) ** 2 < 0.4 ** 2
    z[id] += 0.1

    # Pole 2
    id = (x - 14) ** 2 + (y - 2) ** 2 < 0.4 ** 2
    z[id] += 0.05

    return z


def pole(t):
    if t < 10:
        return 0.0
    elif t > 15:
        return 0.0
    else:
        return 0.05


domain.set_quantity('elevation', topography)  # elevation is a function
domain.set_quantity('friction', 0.01)  # Constant friction
domain.set_quantity('stage', expression='elevation')  # Dry initial condition

# ------------------------------------------------------------------------------
# Setup boundary conditions
# ------------------------------------------------------------------------------
Bi = Dirichlet_boundary([0.1, 0, 0])  # Inflow
Br = Reflective_boundary(domain)  # Solid reflective wall
Bo = Dirichlet_boundary([-5, 0, 0])  # Outflow

domain.set_boundary({'left': Br, 'right': Br, 'top': Br, 'bottom': Br})

# ------------------------------------------------------------------------------
# Evolve system through time
# ------------------------------------------------------------------------------
polygon1 = [[10.0, 0.0], [11.0, 0.0], [11.0, 5.0], [10.0, 5.0]]
polygon2 = [[12.0, 2.0], [13.0, 2.0], [13.0, 3.0], [12.0, 3.0]]

# op1 = Rate_operator(domain, rate=lambda t: 0.5, polygon=polygon2)
op2 = Rate_operator(domain, rate=lambda t: 1, radius=0.4, center=(8.0, 2.0))
op3 = Rate_operator(domain,radius=0.5, center=(16.0, 2.0))


def f1(t):
    return 10


def f2(t):
    if t < 2.5:
        return -5
    else:
        return -10

domain.set_starttime(-0.1)
for t in domain.evolve(yieldstep=0.01, finaltime=0.0):
    domain.print_timestepping_statistics()
    domain.print_operator_timestepping_statistics()

    stage = domain.get_quantity('stage')
    elev = domain.get_quantity('elevation')
    height = stage - elev

    print("hole1 depth: ", height.get_values(interpolation_points=[[8.0, 2.0]]))

for t in domain.evolve(yieldstep=0.1, duration=10.0):
    domain.print_timestepping_statistics()
    domain.print_operator_timestepping_statistics()

    op2.set_rate(f1(t))
    op3.set_rate(f2(t))

    stage = domain.get_quantity('stage')
    elev = domain.get_quantity('elevation')
    height = stage - elev

    print('hole1 depth: ', height.get_values(interpolation_points=[[8.0, 2.0]]))
