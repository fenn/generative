# Particle Simulator
from __future__ import division
import sys, os, pygame, random, math,time
from collections import deque
from pygame.locals import *
pi = math.pi
if sys.platform == 'win32': #for compatibility on some hardware platforms
    os.environ['SDL_VIDEODRIVER'] = 'windib'
    
xmax = 1000    #width of window
ymax = 600     #height of window
psize = 2      #particle size
zoom=1
width=xmax
height=ymax
num_particles=6
time_zoom=5
rainbow=True
ctf = 0.0001
clf = 1
caf = 0.01
class Particle:
   def __init__(self, x = 0, y = 0, dx = 0, dy = 0, phase=0, radius=0, col = (255,255,255), decay=0.999):
       self.x = x+radius*math.cos(phase)    #absolute x,y in pixel coordinates
       self.y = y+radius*math.sin(phase)
       self.old_x, self.old_y = self.x, self.y
       self.rx = x   #absolute x,y in real coordinates
       self.ry = y
       self.dx = dx   #force-like vectors
       self.dy = dy
       self.col = col
       self.radius=radius
       self.phase=phase
       self.decay=decay
       self.start_time=time.time()
       self.r_prime = 1
       self.g_prime = 2
       self.b_prime = 3

   def update(self, points):
       self.old_x, self.old_y = self.x, self.y
       self.radius = 0.5#(time.time()-self.start_time)#**self.decay
       self.x = self.x+time_zoom*self.radius*math.cos(self.phase+time_zoom*(time.time()-self.start_time))    #absolute x,y in pixel coordinates
       self.y = self.y+time_zoom*self.radius*math.sin(self.phase+time_zoom*(time.time()-self.start_time))

   def move(self):
       if self.x <= 0:
           if self.dx < 0: self.dx = -self.dx
       elif self.x >= xmax:
           if self.dx > 0: self.dx = -self.dx
       if self.y <= 0:
           if self.dy < 0: self.dy = -self.dy
       elif self.y >= ymax:
           if self.dy > 0: self.dy = -self.dy
               
       self.rx += self.dx
       self.ry += self.dy
       self.x = int(self.rx + 0.5)
       self.y = int(self.ry + 0.5)

   def draw(self, screen):
        #pygame.draw.line(screen, self.col, (self.old_x, self.old_y), (self.x, self.y), psize)
        #pygame.draw.line(screen, self.col, (self.x-psize, self.y-psize), (self.x, self.y), psize)
        pygame.draw.line(screen, ([x for x in self.col]), (self.old_x*zoom, self.old_y*zoom), (self.x*zoom, self.y*zoom), psize*zoom)
        tmp_time = time_zoom*(time.time()-self.start_time)
        #n = ((self.x - self.old_x)**2 + (self.y - self.old_y)**2)**0.5
        n = self.phase
        if rainbow:
            angle = math.atan2(self.y, self.x)/(2*pi)
            red   = abs(math.sin(2*pi*(self.r_prime/3*ctf*tmp_time+clf*n+caf*angle)))
            green = abs(math.sin(2*pi*(self.g_prime/3*ctf*tmp_time+clf*n+caf*angle)))
            blue =  abs(math.sin(2*pi*(self.b_prime/3*ctf*tmp_time+clf*n+caf*angle)))
            self.col=(255*red, 255*green, 255*blue)

def build_palette():
    "build a color rotation palette. it is a list with 256 RGB triplets"
    #return [(x, x, x) for x in range(256)] #black white gradient
    return [((x*1)%255, (x*2)%255, (x*5)%255) for x in range(256)] 

def rotate_palette(palette, steps):
    '''color rotation palette must be in the format [(0,0,0), ... (x,x,x)] with length 256(?)'''
    rval = deque(palette)
    rval.rotate(steps)
    rval[0]=(0,0,0) #black stays black
    return rval
       
def main():
   # Initialize PyGame
   pygame.init()
   pygame.display.set_caption('Particle Sim')
   screen = pygame.display.set_mode((width, height), pygame.HWSURFACE|pygame.HWPALETTE, 8)
   palette = build_palette()
   screen.set_palette(palette)

   #want fullscreen? pygame.display.set_mode((xmax,ymax), pygame.FULLSCREEN)
   white = (255, 255, 255)
   black = (0,0,0)
   toggle = 0

   particles = []
   for i in range(num_particles):
       if i % 2 > 0: col = white
       else: col = (255,255,0)
#       particles.append( Particle(random.randint(1, xmax-1), random.randint(1, ymax-1), 0, 0, col) )
       #particles.append( Particle(width/2, height/2, 0, 0, i/num_particles,width/10, col) )
       particles.append( Particle(width/2, height/2, 0, 0, i,width/10, col) )

   exitflag = False
   while not exitflag:
       
       # Handle events
       for event in pygame.event.get():
           if event.type == QUIT:
               exitflag = True
           elif event.type == KEYDOWN:
               if event.key == K_ESCAPE or event.key == K_q:
                   exitflag = True
       #screen.fill(white)
       for p in particles:
           p.update(particles)
       #for p in particles:
           #p.move()
	   p.draw(screen)
           #screen.set_palette(rotate_palette(palette, 255*time.time()%1024))	   #pygame.drawrect
           
       if (toggle%10 == 0): 
           pass #toggle = 0
           #screen.set_palette(rotate_palette(palette, 255*(toggle%10)/10)) #255*time.time()%1024))	   #pygame.drawrect
       else: pass 
       toggle += 2
       screen.set_palette(rotate_palette(palette, 255*(toggle%100)/100.)) #255*time.time()%1024))	   #pygame.drawrect
       #time.sleep(time.time()%0.1)    
       pygame.display.flip()

   # Close the Pygame window
   pygame.quit()

#Run the system

if __name__ == "__main__":
    main()
