import anuga
from anuga import rectangular_cross
from anuga import Domain
from anuga.operators.rate_operators import Rate_operator
from anuga import Region
"""
We would use this method to gain the boundary indices
"""
polygon1 = [ [10.0, 0.0], [11.0, 0.0], [11.0, 5.0], [10.0, 5.0] ]
polygon2 = [ [10.0, 0.2], [11.0, 0.2], [11.0, 4.8], [10.0, 4.8] ]

def get_cir (radius=None,center=None,domain=None,size=None,polygons=None):
    if polygons is not None:
        polygon1 = polygons[0]#the larger one
        polygon2 = polygons[1]
        opp1 = Rate_operator(domain, polygon=polygon1)
        opp2 = Rate_operator(domain,polygon = polygon2)
        if isinstance(polygon1, Region):
            opp1.region = polygon1
        else:
            opp1.region = Region(domain, poly=polygon1, expand_polygon=True)
        if isinstance(polygon2, Region):
            opp2.region = polygon2
        else:
            opp2.region = Region(domain, poly=polygon2, expand_polygon=True)



    if radius is not None and center is not None:
        op1 = Rate_operator(domain,radius=radius,center = center)
        op2 = Rate_operator(domain,radius=radius-size,center= center)
        region1 = Region(domain,radius = radius, center = center)
        region2 = Region(domain,radius = radius-size,center = center)
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

