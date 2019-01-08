from math import pi

distance = 32.15
d = 50 - distance/2 - 5
sa = 500
R = 0.1

I = 4.*10.**3./12. + 6.*4.**3./12. + 2*(3.**4.*(pi/8 - 8./9./pi) + pi*3**2/2*(5-0.576*3)**2)

Pa = sa*I*2/d/5/1000
Pm = Pa*(1 + R)/(1-R)

Pmax = Pm + Pa
Pmin = Pm - Pa

print "stress amplitude", sa, 'MPa and R =', R, "results in minimum force", Pmin, 'kN and maximum force', Pmax, 'kN'
