#cython: boundscheck=False

def calculate_z(int maxiter, zs, cs):
    """Calculate output list using Julia update rule"""
    
    cdef unsigned int i, n
    cdef double complex z, c

    output = [0] * len(zs)
    for i in range(len(zs)):
        n = 0
        z = zs[i]
        c = cs[i]
        while n < maxiter and abs(z) < 2:
            z = z * z + c
            n += 1
        output[i] = n
    return output
