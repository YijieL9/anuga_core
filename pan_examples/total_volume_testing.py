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
from anuga import Dirichlet_boundary
from anuga import Domain
from anuga import Reflective_boundary
from anuga.operators.rate_operators import Rate_operator
from anuga import Region
from anuga import rectangular_cross

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

    # inflow pipe hole, located at (2, 2), r = 0.5, depth 0.1
    id = (x - 2) ** 2 + (y - 2) ** 2 < 0.3 ** 2
    z[id] -= 0.2

    # inflow pipe hole, located at (12, 2), r = 0.5, depth 0.1
    id = (x - 12) ** 2 + (y - 2) ** 2 < 0.3 ** 2
    z[id] -= 0.2

    return z


# ------------------------------------------------------------------------------
# Setup initial quantity
# ------------------------------------------------------------------------------
domain.set_quantity('elevation', topography)  # elevation is a function
domain.set_quantity('friction', 0.01)  # Constant friction
domain.set_quantity('stage', expression='elevation')  # Dry initial condition
# --------------------------

"""
We would use this method to gain the boundary indices
"""


# polygon1 = [ [10.0, 0.0], [11.0, 0.0], [11.0, 5.0], [10.0, 5.0] ]
# polygon2 = [ [10.0, 0.2], [11.0, 0.2], [11.0, 4.8], [10.0, 4.8] ]

def get_cir(radius=None, center=None, domain=None, size=None, polygons=None):
    if polygons is not None:
        polygon1 = polygons[0]  # the larger one
        polygon2 = polygons[1]
        opp1 = Rate_operator(domain, polygon=polygon1)
        opp2 = Rate_operator(domain, polygon=polygon2)
        if isinstance(polygon1, Region):
            opp1.region = polygon1
        else:
            opp1.region = Region(domain, poly=polygon1, expand_polygon=True)
        if isinstance(polygon2, Region):
            opp2.region = polygon2
        else:
            opp2.region = Region(domain, poly=polygon2, expand_polygon=True)

    if radius is not None and center is not None:
        op1 = Rate_operator(domain, radius=radius, center=center)
        op2 = Rate_operator(domain, radius=radius - size, center=center)
        region1 = Region(domain, radius=radius, center=center)
        region2 = Region(domain, radius=radius - size, center=center)
        if isinstance(region1, Region):
            op1.region = region1
        else:
            op1.region = Region(domain, poly=region1, expand_polygon=True)
        if isinstance(region2, Region):
            op2.region = region2
        else:
            op2.region = Region(domain, poly=region2, expand_polygon=True)
    if radius is None and center is None:
        indices = [x for x in opp1.region.indices if x not in opp2.region.indices]
    else:
        indices = [x for x in op1.region.indices if x not in op2.region.indices]

    return indices


def get_depth(t):
    # FIXME: according to the index return the overland depth of specific area
    overland_depth = -0.02 * t + 1
    return overland_depth

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
op_inlet = Rate_operator(domain, radius=0.5, center=(2., 2.))
op_outlet = Rate_operator(domain, radius=0.5, center=(12., 2.))  #



from pyswmm import Simulation, Nodes, Links

sim = Simulation('./pipe_test.inp')
sim.start()
node_names = ['Inlet', 'Outlet']

link_names = ['Culvert']

nodes = [Nodes(sim)[names] for names in node_names]
links = [Links(sim)[names] for names in link_names]

# type, area, length, orifice_coeff, free_weir_coeff, submerged_weir_coeff
nodes[0].create_opening(4, 1.0, 1.0, 0.6, 1.6, 1.0)
nodes[0].coupling_area = 1.0

# TODO: setup the outlet node
nodes[1].create_opening(4, 1.0, 1.0, 0.6, 1.6, 1.0)
nodes[1].coupling_area = 1.0


for t in domain.evolve(yieldstep=1.0, finaltime=20.0):
    print(f"coupling step: {t}")
    # domain.print_timestepping_statistics()

    # set the overland_depth
    # TODO: set up the overland depth, modify this function
    nodes[0].overland_depth = get_depth(t)
    print("inlet overland depth: ", get_depth(t))


    volumes = sim.coupling_step(1.0)
    for key in volumes:
        print("Volume total at node", key, ":", volumes[key])
    op_inlet.set_rate(-1 * volumes['Inlet'])
    op_outlet.set_rate(volumes['Outlet'])

    print()