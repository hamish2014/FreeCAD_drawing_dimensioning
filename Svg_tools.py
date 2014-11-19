'''
used for parsing tricky Svg elements such as bezier curves

Beizer code source:      http://www.cs.nyu.edu/~dzorin/numcomp08/bezier.py
Circular fitting ref:    http://wiki.scipy.org/Cookbook/Least_Squares_Circle
'''

import numpy
from numpy import array, mean, linalg, sqrt, pi, linspace, cos, sin

def bezier_cubic_point( p0, p1, p2, p3, t):
    ''' source wikipedia'''
    return p0*(1-t)**3 + 3*p1*t*(1-t)**2 + 3*p2*t**2*(1-t) + t**3 * p3

def bezier_cubic( p0, p1, p2, p3, t):
    ''' source wikipedia'''
    B = numpy.array([
            p0[0]*(1-t)**3 + 3*p1[0]*t*(1-t)**2 + 3*p2[0]*t**2*(1-t) + t**3 * p3[0],
            p0[1]*(1-t)**3 + 3*p1[1]*t*(1-t)**2 + 3*p2[1]*t**2*(1-t) + t**3 * p3[1],
            ])
    return B.transpose()

def fitCircle(X, Y):
    'http://wiki.scipy.org/Cookbook/Least_Squares_Circle, algebraic approximation method'
    x_m = mean(X)
    y_m = mean(Y)
    # calculation of the reduced coordinates
    U = X - x_m
    V = Y - y_m
    # linear system defining the center (uc, vc) in reduced coordinates:
    #    Suu * uc +  Suv * vc = (Suuu + Suvv)/2
    #    Suv * uc +  Svv * vc = (Suuv + Svvv)/2
    Suv  = sum(U*V)
    Suu  = sum(U**2)
    Svv  = sum(V**2)
    Suuv = sum(U**2 *V)
    Suvv = sum(U* V**2)
    Suuu = sum(U**3)
    Svvv = sum(V**3)
    
    # Solving the linear system
    A = array([ [ Suu, Suv ], [Suv, Svv]])
    B = array([ Suuu + Suvv, Svvv + Suuv ])/2.0
    uc, vc = linalg.solve(A, B)

    xc_1 = x_m + uc
    yc_1 = y_m + vc

    # Calcul des distances au centre (xc_1, yc_1)
    Ri_1     = sqrt((X-xc_1)**2 + (Y-yc_1)**2)
    R_1      = mean(Ri_1)
    residu_1 = sum((Ri_1-R_1)**2)
    return xc_1, yc_1, R_1, residu_1

def fitCircle_to_path(P, points_per_segment=6):

    assert len(P[0]) == 1 #i.e. move command
    X = []
    Y = []
    T = linspace(0,1,points_per_segment)
    t0 =    T**0 * (1-T)**3
    t1 = 3* T**1 * (1-T)**2
    t2 = 3* T**2 * (1-T)**1
    t3 =    T**3 * (1-T)**0

    for C in P:
        #print(C)
        if len(C) == 1: #then pen position update
            p3 = C[0]
            continue
        if len(C) == 3: #then cubic Bezier
            p0 = p3
            p1 = C[0]
            p2 = C[1]
            p3 = C[2]
            X = X + ( t0*p0[0] + t1*p1[0] + t2*p2[0] + t3*p3[0] ).tolist()
            Y = Y + ( t0*p0[1] + t1*p1[1] + t2*p2[1] + t3*p3[1] ).tolist()
        if len(C) == 2: #then quadratic Bezier plot, https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Quadratic_B.C3.A9zier_curves
            #\mathbf{B}(t) = (1 - t)^{2}\mathbf{P}_0 + 2(1 - t)t\mathbf{P}_1 + t^{2}\mathbf{P}_2 \mbox{ , } t \in [0,1]. 
            p0 = p3
            p1 = C[0]
            p2 = C[1]
            X = X + ( (1-T)**2*p0[0] + 2*(1-T)*T**p1[0] + T**2*p2[0] ).tolist()
            Y = Y + ( (1-T)**2*p0[1] + 2*(1-T)*T**p1[1] + T**2*p2[1] ).tolist()
            p3 = p2 #move pen; (pens location stored in p3)
    if len(X) > 3:
        return fitCircle(array(X), array(Y))
    else:
        return 0,0,0,10**6

if __name__ == '__main__':
    from matplotlib import pyplot
    print('Testing Bezier plot, source data from http://matplotlib.org/users/path_tutorial.html')
    P = numpy.array( [
            (0., 0.),  # P0
            (0.2, 1.), # P1
            (1., 0.8), # P2
            (0.8, 0.), # P3
            ] )
    pyplot.plot( P[:,0], P[:,1],'--k')

    #B = numpy.array( [ bezier_point_cubic( P[0], P[1], P[2], P[3], t) 
    #      for t in numpy.linspace(0,1,101) ] )
    B = bezier_cubic( P[0], P[1], P[2], P[3], numpy.linspace(0,1,101) )
    pyplot.plot( B[:,0], B[:,1] )

    #print now fitting circle to data
    c_x, c_y, R, R_error = fitCircle( B[:,0], B[:,1])
    T = linspace(0,2*pi)
    X_circle = c_x + cos(T)*R
    Y_circle = c_y + sin(T)*R
    pyplot.plot(  X_circle, Y_circle, 'g-.'  )

    pyplot.axis('equal')

    pyplot.show()
