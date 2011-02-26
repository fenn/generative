#!/usr/bin/python
import copy
import numpy
import Image
import pygame
import cairo
import random
import math
from collections import defaultdict
import psyco

psyco.full()
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

num_particles = 3
sim_time = 50
dt = 1
beta = 0
wobble = .1
max_wobble = 10
scale=2
fatness = 100*scale
min_fatness = 3
branching = True
branch_velocity = 1
max_branches = 2
width = 1024*scale
height = 600*scale
draw_pygame=True
draw_cairo=True
cairo_lines=defaultdict(list)
particles = []  #list of all particles

def sampling(width, height):
    '''really this should probably be a class, but i couldnt figure out how to inherit from numpy.array'''
    return numpy.zeros((width, height), dtype=numpy.int)

def multinomial(pdict):
    '''return an item i from a dict {i:p, j:q} with probability p/(p+q)'''
    ptotal = sum(pdict.values())
    plist = pdict.items()
    a = list(numpy.random.multinomial(1,[p[1]/ptotal for p in plist])) #looks like [0, 0, 1, 0]
    try: return plist[a.index(1)][0]    
    except ValueError: return None

def rotate(vec, theta):
    x, y = vec[0], vec[1]
    theta = 2*math.pi * theta/360
    return numpy.array([x*math.cos(theta)-y*math.sin(theta), x*math.sin(theta)+y*math.cos(theta)], dtype=float)

def random_color():
    rgb = lambda: random.randint(0,255)
    return [rgb(), rgb(), rgb()]

def render_buffer(buffer):
    Image.frombuffer('L',(width, height), numpy.array(buffer*255, dtype=numpy.uint8).data, 'raw', 'L', 0, 1).save(open('buffer.png','w'))
    
def screenshot():
    global surface, cr
    f = open('pygame_screenshot.png', 'w')
    if draw_pygame:
        pygame.image.save(pygame.display.get_surface(), f)
        print "saved pygame screenshot"
    if draw_cairo:  #bleck
        max_len=0
        for particle in particles: max_len = max(max_len, len(cairo_lines[particle]))
        for n in range(max_len-3): #only works if all traces have same number of segments?
            for particle in particles:
                trace = cairo_lines[particle]
                cr.set_line_join(cairo.LINE_JOIN_ROUND)
                if n == 0: cr.set_line_cap(cairo.LINE_CAP_ROUND)
                else: cr.set_line_cap(cairo.LINE_CAP_BUTT)
                cr.move_to(trace[0][0][0], trace[0][0][1])
                try:
                    cr.set_line_width(trace[n][2]+8)
                    cr.move_to(trace[n][0][0], trace[n][0][1])
                    cr.line_to(trace[n+1][0][0], trace[n+1][0][1])
                    cr.line_to(trace[n+2][0][0], trace[n+2][0][1])
                    cr.line_to(trace[n+3][0][0], trace[n+3][0][1])
                    cr.set_source_rgba(0,0,0,1)
                    cr.stroke_preserve()
                    cr.set_line_width(trace[n][2])
                    cr.set_source_rgba(particle.color[0], particle.color[1], particle.color[2], 1)
                    cr.stroke()
                except IndexError: pass
        surface.write_to_png('cairo_screenshot.png')
        surface.finish()
        print "saved cairo screenshot"
        
class Particle:
    def __init__(self, position=[0,0], velocity = [0,0], line_width=1, color=[0,0,0], parent = None, charge = 1, mass = 1):
        global particles
        try: self.id = particles[-1].id+1
        except IndexError: self.id=0
        self.velocity = numpy.array(velocity, dtype=float)
        self.position =numpy.array(position, dtype=float)
        self.old_position = position
        self.color = color
        self.charge = charge
        self.mass = mass
        self.line_width = line_width
        self.decay_types = {}
        self.age = 0
        self.age_ticks = 0
        self.toggle = True
        self.path_integral = 0
        self.baby = None
        self.parent = parent
        self.speed = 1
        self.rank = 0
        self.decay_probability = 0.001
        particles.append(self)
    def update(self, particles, dt=1):
        '''will need to change this to update all particles at once for speed'''
        self.old_position = copy.copy(self.position)
        self.age +=dt
        self.age_ticks +=1
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        for p in particles:
            if p.parent == self or self.parent == p: attract = -.2
            else: attract = 1
            dx = p.position[0] - self.position[0]
            dy = p.position[1] - self.position[1]
            d = math.sqrt(dx**2 + dy**2)
            if d == 0: d=1
            self.velocity[0] += attract * dx / (self.mass * d**2) #inverse square law
            self.velocity[1] += attract * dy / (self.mass * d**2)
            self.velocity = rotate(self.velocity, beta*self.charge+random.uniform(-1*wobble,wobble)*min(self.speed**2, max_wobble))
            #self.velocity = rotate(self.velocity, beta*self.charge+random.uniform(-1*wobble,wobble))
            self.speed = math.sqrt(self.velocity[0]**2+self.velocity[1]**2)+0.01 #just keeping track
        for i in range(3):
            self.color[i] = (self.color[i]+0.001)% 255
        self.decay()
    def decay(self):
        if random.uniform(0,1)>= 1-self.decay_probability:
            print 'decay:', multinomial(self.decay_types)
            
    def branch(self):
        if not branching: return
        baby = Particle(position=self.position, velocity=self.velocity, color=self.color, line_width=self.line_width, parent=self)
        baby.velocity = self.velocity
        baby.age = self.age
        baby.speed = self.speed
        baby.toggle = False
        self.rank += 1
        baby.rank = self.rank
#        self.mass = self.mass/1.2
#        baby.mass = self.mass
        self.baby = baby
        particles.append(baby)
        baby.velocity =  branch_velocity*rotate(baby.velocity, self.branch_angle) 
        self.velocity = branch_velocity*rotate(self.velocity, -1*self.branch_angle) 
        #print 'branch', self.age
        
    def draw(self, buffer=buffer, screen=None, cr=None):
        global cairo_lines
        #x_binned, y_binned = int(self.position[0]), int(self.position[1])
        #print "particle #%d x: %.2f, y: %.2f, mx: %.2f, my: %.2f" % (particles.index(self), self.position[0], self.position[1], self.velocity[0], self.velocity[1])
        #if x_binned < width and y_binned < height and x_binned >= 0 and y_binned >= 0:
        #    buffer[x_binned][y_binned] += self.mass
        #line_width = min(fatness, dt*fatness/(math.log(self.age_ticks+1)*self.speed)+1)
        #line_width = min(fatness, dt*fatness/(self.age**2+1)*self.speed+min_fatness)
        #line_width = min(fatness, dt*fatness/(((self.rank)**2+1)*self.speed)+min_fatness)
        line_width = min(fatness, fatness/(((self.age**0.5)+1)*(self.speed+1)*dt)+min_fatness)
        outline_width = line_width + 4
        start, end = (self.old_position[0], self.old_position[1]), (self.position[0], self.position[1])
        if draw_pygame:
            pygame.draw.line(screen, (0,0,0), start, end, outline_width)
            pygame.draw.line(screen, self.color, start, end, line_width)
            if draw_cairo:
                cairo_lines[self].append((start, end, line_width))


class Neuron(Particle):
    def __init__(self, *args, **kwargs):
        Particle.__init__(self, *args, **kwargs)
        self.decay_types = {Soma:1}

class Soma(Particle):
    def __init__(self, *args, **kwargs):
        Particle.__init__(self, *args, **kwargs)
        self.decay_types = {Dendrite: 0.1,
                                        Axon: 0.9}
        self.decay_probability = 0.001
    def update(self):
        self.age += dt


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
    white = [255, 255, 255]
    black = [0,0,0]
    
    #initialize cairo
    surface = cairo.SVGSurface('cairo_screenshot.svg', width, height)
    cr = cairo.Context(surface)
    cr.translate(0.5, 0.5)
    cr.set_source_rgba(0,0,0,0)
    cr.rectangle(0,0,width,height)
    cr.fill()  
    
    for i in range(num_particles):
        if i % 2 > 0: 
            col = white
            charge = 1
            mass = 1
        else: 
            col = [255,255,0]
            charge = -1
            mass =1
        col = random_color()
        p = Neuron((random.randint(1, width-1), random.randint(1, height-1)), color=col, charge = charge, mass=mass)
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