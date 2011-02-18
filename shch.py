#!/usr/bin/python
import copy
import numpy
import Image
import pygame
import random
import math
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
dt = 30
scale=2
fatness = 20*scale
width = 1024*scale
height = 600*scale

def sampling(width, height):
    '''really this should probably be a class, but i couldnt figure out how to inherit from numpy.array'''
    return numpy.zeros((width, height), dtype=numpy.int)

def render_buffer(buffer):
    Image.frombuffer('L',(width, height), numpy.array(buffer*255, dtype=numpy.uint8).data, 'raw', 'L', 0, 1).save(open('buffer.png','w'))
    
def screenshot():
    f = open('screenshot.png', 'w')
    pygame.image.save(pygame.display.get_surface(), f)
    print "saved screenshot"
        
class Particle:
    def __init__(self, position=[0,0], momentum = [0,0], line_width=1, color=(0,0,0), parent = None):
        global particles
        self.momentum = numpy.array(momentum, dtype=float)
        self.position = numpy.array(position, dtype=float)
        self.old_position = position
        self.color = color
        self.mass = 1
        self.line_width = 1
        self.decay_types = []
        particles.append(self)
    def update(self, particles, dt=1):
        '''will need to change this to update all particles at once for speed'''
        self.old_position = copy.copy(self.position)
        self.position[0] += self.momentum[0] * dt
        self.position[1] += self.momentum[1] * dt
        for p in particles:
            dx = p.position[0] - self.position[0]
            dy = p.position[1] - self.position[1]
            d = math.sqrt(dx**2 + dy**2)
            if d == 0: d=1
            self.momentum[0] += dx / d**2 #inverse square law
            self.momentum[1] += dy / d**2
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

def main():
    #foo = Particle([0,0],[.2,.1])
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    
    blah = '''for step in range(sim_time/dt):
        for particle in particles: 
            particle.update(dt)
            particle.draw(buffer)
    #        print buffer
    #        time.sleep(0.1)
    print buffer
    for particle in particles: particle.draw(buffer)
    #render_buffer(buffer)'''

    # Initialize PyGame
    pygame.init()
    pygame.display.set_caption('Particle Sim')
    screen = pygame.display.set_mode((width, height))
    white = (255, 255, 255)
    black = (0,0,0)

    for i in range(20):
        if i % 2 > 0: col = white
        else: col = (255,255,0)
        p = Particle((random.randint(1, width-1), random.randint(1, height-1)), color=col)
        #particles.append(p)

    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    pygame.quit()
                if event.key == pygame.K_s:
                    screenshot()
        #screen.fill(white)
        for p in particles:
            p.update(particles, dt)
            velocity = math.sqrt(p.momentum[0]**2+p.momentum[1]**2)+0.01
            line_width = min(fatness, int(fatness/velocity)+1)
            start, end = (int(p.old_position[0]), int(p.old_position[1])), (int(p.position[0]), int(p.position[1]))
            pygame.draw.line(screen, black, start, end, line_width+8) #outline
            pygame.draw.line(screen, p.color, start, end, line_width)
        pygame.display.flip()


if __name__ == '__main__':
    main()