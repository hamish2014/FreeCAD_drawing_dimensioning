"""conjugate gradient optimisation method using Polak-Ribiere search directions (CGPR)"""
from numpy import array, zeros, nan, dot, inf
from numpy.linalg import norm
from numpy.random import rand
from lineSearches import quadraticLineSearch


def toStdOut(txt):
    print(txt)

def CGPR( x0, f, grad_f, x_tol=10**-6, f_tol=None, maxIt=100,
          debugPrintLevel=0, printF=toStdOut, lineSearchIt=20):
    '''
    search for minimum using conjugate gradient optimisation with Polak-Ribiere search directions 
    '''
    n = len(x0)
    x = array(x0)
    x_c = zeros(n) * nan
    u_hist = []
    g = nan
    for i in range(maxIt):
        f_x = f(x)
        printF('cgpr it %02i: norm(prev. step) %1.1e,  f(x) %1.3e' % (i, norm(x_c), f_x))
        if debugPrintLevel > 1:
            printF('  x    %s' % x)
            printF('  f(x) %s' % f_x)
        if norm(x_c) <= x_tol:
            break
        if f_x < f_tol:
            break
        grad_prev = g
        g = grad_f(x, f0=f_x)
        if debugPrintLevel > 1:
            printF('  grad_f : %s' % g) 
        if i == 0:
            u = -g
            u_hist = [u]
        else:
            beta = dot(g - grad_prev,g) / norm(grad_prev)**2
            u = -g + beta*u_hist[-1]
            u_hist.append(u)
        if debugPrintLevel > 1:
            printF('  u    %s' % u)
        x_next =  quadraticLineSearch( f, x, f_x, u, lineSearchIt, debugPrintLevel-2, printF, tol_x=x_tol, tol_stag=inf )
        x_c = x_next - x
        x = x_next
    return x



class GradientApproximatorForwardDifference:
    def __init__(self, f):
        self.f = f
    def __call__(self, x, f0, eps=10**-7):
        n = len(x)
        grad_f = zeros(n)
        for i in range(n):
            x_eps = x.copy()
            x_eps[i] = x_eps[i] + eps
            grad_f[i] = (self.f(x_eps) - f0)/eps
        return grad_f

if __name__ == '__main__':
    print('Testing CGPR algorithm')
    print('-GradientApproximator-')
    def f(X) :
        y,z=X
        return y + y*z + (1.0-y)**3
    def grad_f(X):
        y,z=X
        return  array([ 1 + z - 3*(1.0-y)**2, y ])
    grad_f_fd = GradientApproximatorForwardDifference(f)
    for i in range(2):
        X = rand(2)*10-5
        print('    X %s' % X)
        print('    grad_f(X) analytical:   %s' % grad_f(X))
        print('    grad_f(X) forwardDiff.: %s' % grad_f_fd(X, f(X)))
        print('  norm(analytical-forwardDiff) %e' % norm(grad_f(X) - grad_f_fd(X, f(X))) )

    def f_basic(X):
        y,z = X
        return 2*(y-3)**2 + 2*(z+1)**2

    CGPR( -10+rand(2), f_basic, GradientApproximatorForwardDifference(f_basic),
          debugPrintLevel=3, printF=toStdOut, lineSearchIt=5)

    def f1(x) :
        "Rosenbrocks's parabloic valley "
        x1,x2 = x[0],x[1]
        return 100*(x2 -x1 **2) ** 2 + (1 - x1)**2
    def f2(x) :
        "Quadratic function"
        x1,x2 = x[0],x[1]
        return (x1 + 2*x2 - 7)**2 + (2*x1 + x2 - 5)**2 
    def f3(x) :
        "Powells Quadratic function"
        x1,x2,x3,x4 = x[0],x[1],x[2],x[3]
        return (x1 + 10*x2)**2 + 5 * (x3 - x4)**2 + (x2 - 2*x3)**4 + 10*(x1-x4)**4

    for t,n in zip( [f1,f2,f3], [2,2,4]):
        print(t.__doc__)
        x0 =  -10+20*rand(n)
        CGPR( x0, t, GradientApproximatorForwardDifference(t),
              debugPrintLevel=1, printF=toStdOut, lineSearchIt=20)
