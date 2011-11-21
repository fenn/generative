# Particle Simulator
from __future__ import division
import sys, os, pygame, math, time
from collections import deque
from pygame.locals import *
pi = math.pi
if sys.platform == 'win32': #for compatibility on some hardware platforms
    os.environ['SDL_VIDEODRIVER'] = 'windib'
    
width = 1000
height = 600
particle_size = 4
zoom=1
epicycle_radius = 15
num_particles=500
time_zoom=0.25
rainbow=True
color_rotation=True
color_rotation_speed=20
palette_size=4096
ctf = 0.1 #color time frequency
clf = 50/num_particles # color length frequency - actually this colors the point based on order of creation
caf = 10.01 # color angle frequency - color depends on angle relative to center

class Particle:
   def __init__(self, x = 0, y = 0, dx = 0, dy = 0, phase=0, radius=0, color = (255,255,255), decay=0.999):
       self.x = x+radius*math.cos(phase)    #absolute x,y in pixel coordinates
       self.y = y+radius*math.sin(phase)
       self.old_x, self.old_y = self.x, self.y
       self.color = color
       self.radius=radius
       self.phase=phase
       self.decay=decay
       self.start_time=time.time()
       self.r_prime = 1
       self.g_prime = 2
       self.b_prime = 3
       self.next, self.prev = None, None


   def update(self, points):
       self.old_x, self.old_y = self.x, self.y
       #self.radius = (time.time()-self.start_time)**self.decay
       self.x = self.x+time_zoom*self.radius*math.cos(self.phase+time_zoom*(time.time()-self.start_time))    #absolute x,y in pixel coordinates
       self.y = self.y+time_zoom*self.radius*math.sin(self.phase+time_zoom*(time.time()-self.start_time))

   def draw(self, screen):
        #vel = ((self.x - self.old_x)**2 + (self.y - self.old_y)**2)**0.5
        angle = math.atan2(self.y-height/2, self.x-width/2)/(2*pi)
	if (angle + 0.7)% 1 < (time.time()-self.start_time)*time_zoom % 1: angle = 0 #spiral cuts between clf and caf
        pygame.draw.line(screen, self.color, (self.old_x*zoom, self.old_y*zoom), (self.x*zoom, self.y*zoom), particle_size*zoom)
        tmp_time = time_zoom*(time.time()-self.start_time)
        n = self.phase
        if rainbow:
            red   = abs(math.sin(2*pi*(self.r_prime/3*ctf*tmp_time+clf*n+caf*angle)))
            green = abs(math.sin(2*pi*(self.g_prime/3*ctf*tmp_time+clf*n+caf*angle)))
            blue =  abs(math.sin(2*pi*(self.b_prime/3*ctf*tmp_time+clf*n+caf*angle)))
            self.color=(255*red, 255*green, 255*blue)

def build_palette():
    "build a color rotation palette. it is a list of RGB triplets"
    #return [(x, x, x) for x in range(255)] #black white gradient
    mysin = lambda x: (math.sin(x*2*pi)+1)*255
    return [(mysin(x*.011)%255, mysin(x*.0012)%255, mysin(x*.0013)%255) for x in range(palette_size)] 

def rotate_palette(palette, steps):
    '''color rotation palette must be in the format [(0,0,0), ... (x,x,x)] with length 256(?)'''
    rval = deque(palette)
    rval.rotate(int(steps))
    rval[0]=(0,0,0) #black stays black
    return list(rval)[0:255]    
       
def main():
   # Initialize PyGame
   pygame.init()
   pygame.display.set_caption('Particle Sim')
   screen = pygame.display.set_mode((width, height), pygame.HWSURFACE|pygame.HWPALETTE, 8)
   palette = build_palette()
   screen.set_palette(palette)

   #want fullscreen? pygame.display.set_mode((width,height), pygame.FULLSCREEN)
   white = (255, 255, 255)
   black = (0,0,0)
   toggle = 0

   particles = []
   for i in range(num_particles):
       if i % 2 > 0: color = white
       else: color = (255,255,0)
       p = Particle(width/2, height/2, 0, 0, 2*pi*i/num_particles,epicycle_radius, color)
       try: 
         tail = particles[-1:][0] # get last element from list
         p.prev = tail
         tail.next = p
       except IndexError: pass 
       particles.append(p)
      

   exitflag = False
   while not exitflag:
       
       # Handle events
       for event in pygame.event.get():
           if event.type == QUIT:
               exitflag = True
           elif event.type == KEYDOWN:
               if event.key == K_ESCAPE or event.key == K_q:
                   exitflag = True

       for p in particles:
           p.update(particles)
	   p.draw(screen)

       toggle += color_rotation_speed
       if color_rotation:
         screen.set_palette(rotate_palette(palette, color_rotation_speed*time.time()%palette_size))
       #time.sleep(time.time()%0.1)    
       pygame.display.flip()

   pygame.quit()

if __name__ == "__main__":
    main()
