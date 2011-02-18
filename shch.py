#!/usr/bin/python
import copy
import numpy

'''
shch generative system
----------------------

a particle has:
inertia and an impulse imparted to it
line width
list of possible decay types

a particle continues on its path or can decay into a different particle type:
root - probability of a root depends on local curvature of starting image
branch - maintains original particle, new particle has same characteristics
leaf - line width increases/decreases according to some function, with a given spiral angle


two behaviors, one type follows the local offset, the other goes in a circle or spiral
this can be attained by setting the impulse imparted to a function of the local conditions
'''

particles = []  #list of all particles
sim_time = 50
dt = .1

width = 20
height = 10

def sampling(width, height):
    '''really this should probably be a class, but i couldnt figure out how to inherit from numpy.array'''
    return numpy.zeros((width, height), dtype=numpy.int)

class Particle:
    def __init__(self, position=[0,0], momentum = [0,0], line_width=1, parent = None):
        global particles
        self.momentum = numpy.array(momentum, dtype=float)
        self.position = numpy.array(position, dtype=float)
        self.mass = 1
        self.line_width = 1
        self.decay_types = []
        particles.append(self)
    def step(self, dt=1):
        '''will need to change this to update all particles at once for speed'''
        self.position[0] += self.momentum[0] * dt
        self.position[1] += self.momentum[1] * dt
    def branch(self):
        baby = Particle(self.position, self.momentum, self.line_width, self)
        particles.append(baby)
    def draw(self, buffer):
        x_binned, y_binned = int(self.position[0]), int(self.position[1])
        print "particle #%d x: %.2f, y: %.2f, mx: %.2f, my: %.2f" % (particles.index(self), self.position[0], self.position[1], self.momentum[0], self.momentum[1])
        if x_binned < width and y_binned < height and x_binned >= 0 and y_binned >= 0:
            print 'hi'
            buffer[x_binned][y_binned] += self.mass

buffer = sampling(width, height)

if __name__ == '__main__':
    foo = Particle([0,0],[.2,.1])
    import time
    for step in range(sim_time/dt):
        for particle in particles: 
            particle.step(dt)
            particle.draw(buffer)
            print buffer
            time.sleep(0.1)
    print buffer
    for particle in particles: particle.draw(buffer)
    print buffer
    