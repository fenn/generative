#!/usr/bin/python
from __future__ import division
import copy
import numpy
import Image
import pygame
import cairo
import random
import math
from collections import defaultdict
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
dt = 3
scale=2
fatness = 20*scale
width = 1024*scale
height = 600*scale
draw_pygame=True
draw_cairo=True
cairo_lines=defaultdict(list)

def sampling(width, height):
    '''really this should probably be a class, but i couldnt figure out how to inherit from numpy.array'''
    return numpy.zeros((width, height), dtype=numpy.int)

def render_buffer(buffer):
    Image.frombuffer('L',(width, height), numpy.array(buffer*255, dtype=numpy.uint8).data, 'raw', 'L', 0, 1).save(open('buffer.png','w'))
    
def screenshot():
    global surface, cr
    f = open('pygame_screenshot.png', 'w')
    if draw_pygame:
        pygame.image.save(pygame.display.get_surface(), f)
        print "saved pygame screenshot"
    if draw_cairo:  #bleck
        for particle in particles:
            trace = cairo_lines[particle]
            n=0; dn=1
            max_n = len(trace)
            while n+dn < len(trace):
                a = (n/max_n)
                cr.set_line_cap(cairo.LINE_CAP_BUTT)
                cr.set_line_join(cairo.LINE_JOIN_MITER)
                try:
                        #do outline along 2 segments
                        dx, dy, dn = 0, 0, 1
                        cr.set_line_width(trace[n][2]+8)
                        cr.set_line_cap(cairo.LINE_CAP_BUTT)
                        cr.move_to(trace[n][0][0], trace[n][0][1])
                        #really short moves makes antialiased garbage
                        while abs(dx) <4 and abs(dy) <4 and dn < 100 and n+dn<len(trace):
                            dx = trace[n+dn][0][0] - trace[n][0][0]
                            dy = trace[n+dn][0][1] - trace[n][0][1]
                            dn += 1
                        if n+dn > len(trace): break
                        print dx, dy, dn
                        cr.rel_line_to(2*dx, 2*dy)
                        #cr.line_to(trace[n+dn][0][0], trace[n+dn][0][1])
                        cr.set_source_rgba(0,0,0, 1)
                        cr.stroke()
                        cr.set_source_rgba(particle.color[0], particle.color[1], particle.color[2], 1)
                        cr.set_line_width(trace[n][2])
                        #paint colored fill over 4 (or more) segments to cover antialiasing junk
                        cr.set_line_cap(cairo.LINE_CAP_BUTT)
                        cr.move_to(trace[n-dn][0][0], trace[n-dn][0][1])
                        cr.rel_line_to(dx, dy)
                        cr.rel_line_to(dx, dy)
                        #cr.line_to(trace[n][0][0], trace[n][0][1])
                        #cr.line_to(trace[n+dn][0][0], trace[n+dn][0][1])
                        #cr.line_to(trace[n+2*dn][0][0], trace[n+2*dn][0][1])
                        cr.stroke()
                except IndexError: print 'overshoot:', n, 'out of', max_n, 'particle', particles.index(particle), 'dn', dn, 'velocity', trace[n][2]
                n += dn
        #print cairo_lines.items()[0]
        surface.write_to_png('cairo_screenshot.png')
        surface.finish()
        print "saved cairo screenshot"
        
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
    def draw(self, buffer=buffer, screen=None, cr=None):
        global cairo_lines
        #x_binned, y_binned = int(self.position[0]), int(self.position[1])
        #print "particle #%d x: %.2f, y: %.2f, mx: %.2f, my: %.2f" % (particles.index(self), self.position[0], self.position[1], self.momentum[0], self.momentum[1])
        #if x_binned < width and y_binned < height and x_binned >= 0 and y_binned >= 0:
        #    buffer[x_binned][y_binned] += self.mass
        velocity = math.sqrt(self.momentum[0]**2+self.momentum[1]**2)+0.01
        line_width = min(fatness, fatness/velocity+1)
        outline_width = line_width + 8
        start, end = (self.old_position[0], self.old_position[1]), (self.position[0], self.position[1])
        if draw_pygame:
            pygame.draw.line(screen, (0,0,0), start, end, outline_width)
            pygame.draw.line(screen, self.color, start, end, line_width)
            if draw_cairo:
                cairo_lines[self].append((start, end, line_width))


buffer = sampling(width, height)

def main():
    global surface, cr
    #foo = Particle([0,0],[.2,.1])
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    
    # Initialize PyGame
    pygame.init()
    pygame.display.set_caption('Particle Sim')
    screen = pygame.display.set_mode((width, height))
    white = (255, 255, 255)
    black = (0,0,0)
    
    #initialize cairo
    surface = cairo.SVGSurface('cairo_screenshot.svg', width, height)
    cr = cairo.Context(surface)
    cr.translate(0.5, 0.5)
    cr.set_source_rgba(0,0,0,0)
    cr.rectangle(0,0,width,height)
    cr.fill()  
    cr.rectangle(0,0,100,100)
    cr.set_source_rgba(1,1,1,1)
    cr.fill()
    
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
            p.draw(buffer=buffer,screen=screen, cr=cr)
        pygame.display.flip()


if __name__ == '__main__':
    main()