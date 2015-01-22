'''
used for parsing tricky Svg elements such as bezier curves

Beizer code source:      http://www.cs.nyu.edu/~dzorin/numcomp08/bezier.py
Circular fitting ref:    http://wiki.scipy.org/Cookbook/Least_Squares_Circle
'''

import numpy
from numpy import array, mean, linalg, sqrt, pi, linspace, cos, sin, arctan2

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

    X = []
    Y = []
    T = linspace(0,1,points_per_segment)
    t0 =    T**0 * (1-T)**3
    t1 = 3* T**1 * (1-T)**2
    t2 = 3* T**2 * (1-T)**1
    t3 =    T**3 * (1-T)**0

    for C in P:
        #print(C)
        if len(C) == 4: #then cubic Bezier
            p0, p1, p2, p3 = C
            X = X + ( t0*p0[0] + t1*p1[0] + t2*p2[0] + t3*p3[0] ).tolist()
            Y = Y + ( t0*p0[1] + t1*p1[1] + t2*p2[1] + t3*p3[1] ).tolist()
        if len(C) == 3: #then quadratic Bezier plot, https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Quadratic_B.C3.A9zier_curves
            #\mathbf{B}(t) = (1 - t)^{2}\mathbf{P}_0 + 2(1 - t)t\mathbf{P}_1 + t^{2}\mathbf{P}_2 \mbox{ , } t \in [0,1]. 
            p0, p1, p2 = C
            X = X + ( (1-T)**2*p0[0] + 2*(1-T)*T**p1[0] + T**2*p2[0] ).tolist()
            Y = Y + ( (1-T)**2*p0[1] + 2*(1-T)*T**p1[1] + T**2*p2[1] ).tolist()
    if len(X) > 3:
        return fitCircle(array(X), array(Y))
    else:
        return 0,0,0,10**6

def findCircularArcCentrePoint(r, x_1, y_1, x_2, y_2, largeArc, sweep, debug=False ):
    '''
    (x_1 - x_c)**2 + (y_1 - y_c)**2 = r**2  (1)
    (x_2 - x_c)**2 + (y_2 - y_c)**2 = r**2  (2)
    giving 2 posible centre points from, that is where largeArc and Sweep come in
    using geometry to solve for centre point...

    large arc flag - is 0 if an arc spanning less than or equal to 180 degrees is chosen, or 1 if an arc spanning greater than 180 degrees is chosen.
    sweep flag     - is 0 if the line joining center to arc sweeps through decreasing angles, or 1 if it sweeps through increasing angles.

    '''
    from numpy import arccos, arctan2, sin, cos, pi
    # the law of cosines states c^2 = a^2 + b^2 - 2ab*cos(gamma)
    c,a = r,r
    b = ( ( x_2-x_1 )**2 + ( y_2-y_1 )**2 ) ** 0.5
    cos_gamma = ( a**2 + b**2 - c**2 ) / ( 2*a*b )
    if -1 <= cos_gamma and cos_gamma < 1:
        gamma = arccos( cos_gamma ) #angle + pi radians = other possible centre point
    else:
        return numpy.nan, numpy.nan
    if debug: print('x1,y1 : %1.2f, %1.2f' % (x_1, y_1))
    if debug: print('x2,y2 : %1.2f, %1.2f' % (x_2, y_2))
    if debug: print('large arc : %s' % largeArc)
    if debug: print('sweep     : %s' % sweep ) 
    if debug: print('x2,y2 : %1.2f, %1.2f' % (x_2, y_2))
    if debug: print('gamma %3.1f' % (gamma/pi*180))
    

    angle_1_2 = arctan2( y_2 - y_1, x_2 - x_1) #range ``[-pi, pi]``
    # taking possible centre and testing it
    c_x = x_1 + r*cos(angle_1_2 + gamma)
    c_y = y_1 + r*sin(angle_1_2 + gamma)
    if debug: print('possible c_x,c_y at %1.2f, %1.2f' % (c_x, c_y))
    c_x_alt = x_1 + r*cos(angle_1_2 - gamma)
    c_y_alt = y_1 + r*sin(angle_1_2 - gamma)
    if debug: print('      or c_x,c_y at %1.2f, %1.2f' % (c_x_alt, c_y_alt))

    angle_1 = arctan2( y_1 - c_y, x_1 - c_x)
    angle_2 = arctan2( y_2 - c_y, x_2 - c_x)
    if debug: print('  angle_1 %3.1f deg' % (angle_1 / pi * 180))
    if debug: print('  angle_2 %3.1f deg' % (angle_2 / pi * 180))
    if not largeArc:
        if abs(angle_1 - angle_2) > pi:
            if angle_1 < angle_2:
                angle_1 = angle_1 + 2*pi
            else:
                angle_2 = angle_2 + 2*pi
    else:
        if abs(angle_1 - angle_2) < pi:
            if angle_1 < angle_2:
                angle_1 = angle_1 + 2*pi
            else:
                angle_2 = angle_2 + 2*pi
    if debug: print('after largeArc flag correction')
    if debug: print('  angle_1 %3.1f deg' % (angle_1 / pi * 180))
    if debug: print('  angle_2 %3.1f deg' % (angle_2 / pi * 180))
    if sweep:
        correctCentre = angle_2 > angle_1
    else:
        correctCentre = angle_2 < angle_1
    if correctCentre:
        return c_x, c_y
    else:
        return c_x_alt,  c_y_alt 

def pointsAlongCircularArc(r, x_1, y_1, x_2, y_2, largeArc, sweep, noPoints, debug=False ):
    'excluding first points'
    c_x, c_y = findCircularArcCentrePoint(r, x_1, y_1, x_2, y_2, largeArc, sweep, debug)
    angle_1 = arctan2( y_1 - c_y, x_1 - c_x)
    angle_2 = arctan2( y_2 - c_y, x_2 - c_x)
    if not sweep: # arc sweeps through increasing angles
        if angle_2 > angle_1:
            angle_2 = angle_2 - 2*pi
    else:
        if angle_1 > angle_2:
            angle_2 = angle_2 + 2*pi
    points = []
    for i in range(1,noPoints+1):
        a = angle_1 + (angle_2 - angle_1) * 1.0*i/noPoints
        points.append([ 
                c_x + r*cos(a), 
                c_y + r*sin(a)
                ])
    return points
    
def toStdOut(txt):
    print(txt)

def fitCircleNumerically( X, Y, printF=toStdOut ):
    from cgpr import CGPR, GradientApproximatorForwardDifference
    X = array(X)
    Y = array(Y)
    def f(x):
        #c_x, c_y = x #not working as planning
        c_x, c_y, r = x
        D = (X - c_x)**2 + (Y - c_y)**2 - r**2
        return linalg.norm(D)

    grad_f = GradientApproximatorForwardDifference(f)
    #initial guess 
    x0 = numpy.array([0.0, 0.0, 1.0])
    xOpt = CGPR( x0, f, grad_f, debugPrintLevel=2, printF=printF, lineSearchIt=20 )
    error = f(xOpt)
    c_x, c_y, R = xOpt
    #R = mean( (X - c_x)**2 + (Y - c_y)**2)
    return c_x, c_y, R, error


if __name__ == '__main__':
    from matplotlib import pyplot
    from numpy.random import rand
    
    print('testing circle lib')

    P = numpy.array( [
            (0., 0.),  # P0
            (0.2, 1.), # P1
            (1., 0.8), # P2
            (0.8, 0.), # P3
            ] )
    pyplot.plot( P[:,0], P[:,1],'--k')
    pyplot.title('Bezier plot, source data from http://matplotlib.org/users/path_tutorial.html')

    #B = numpy.array( [ bezier_point_cubic( P[0], P[1], P[2], P[3], t) 
    #      for t in numpy.linspace(0,1,101) ] )
    B = bezier_cubic( P[0], P[1], P[2], P[3], numpy.linspace(0,1,101) )
    pyplot.plot( B[:,0], B[:,1] )

    #print now fitting circle to data
    c_x, c_y, R, R_error = fitCircle( B[:,0], B[:,1])

    def plotCircle( cx, cy, R, style):
        T = linspace(0,2*pi)
        X = c_x + cos(T)*R
        Y = c_y + sin(T)*R
        pyplot.plot(  X, Y, style  )
    plotCircle( c_x, c_y, R, 'g-.')

    pyplot.axis('equal')

    pyplot.figure()
    n = 20
    for i, angleUpperlimit in enumerate(numpy.array([45, 90, 180, 270])*pi/180):
        r = 10 + 40*rand()
        angles = rand(n)*angleUpperlimit
        c_x, c_y = 42*rand(2) - 21
        X = c_x + cos(angles)*r + rand(n)
        Y = c_y + sin(angles)*r
        pyplot.subplot(2,2,i+1)
        pyplot.plot( X, Y,'go')
        c_x, c_y, R, R_error = fitCircle( X, Y)
        plotCircle( c_x, c_y, R, 'g:')
        c_x, c_y, R, R_error = fitCircleNumerically( X, Y)
        plotCircle( c_x, c_y, R, 'b--')
        pyplot.axis('equal')


    pyplot.show()

