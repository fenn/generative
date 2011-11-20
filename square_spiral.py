# Particle Simulator

import sys, os, pygame, random, math,time
from pygame.locals import *

if sys.platform == 'win32': #for compatibility on some hardware platforms
    os.environ['SDL_VIDEODRIVER'] = 'windib'
    
xmax = 1000    #width of window
ymax = 600     #height of window
psize = 3      #particle size
width=xmax
height=ymax


class Particle:
   def __init__(self, x = 0, y = 0, dx = 0, dy = 0, phase=0, radius=0, col = (255,255,255), decay=0.9):
       self.x = x+radius*math.cos(phase+time.time())    #absolute x,y in pixel coordinates
       self.y = y+radius*math.sin(phase+time.time())
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

   def update(self, points):
       self.old_x, self.old_y = self.x, self.y
       self.radius = (time.time()-self.start_time)**self.decay
       self.x = self.x+self.radius*math.cos(self.phase+time.time())    #absolute x,y in pixel coordinates
       self.y = self.y+self.radius*math.sin(self.phase+time.time())

       dx = 0.0
       dy = 0.0
       for p in points:         #where is everybody else?
           dx1 = p.rx - self.rx
           dy1 = p.ry - self.ry
           
           d = math.sqrt(dx1**2 + dy1**2)   #distance from me to p

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
        pygame.draw.line(screen, self.col, (self.x-psize, self.y-psize), (self.x, self.y), psize)

       
def main():
   # Initialize PyGame
   pygame.init()
   pygame.display.set_caption('Particle Sim')
   screen = pygame.display.set_mode((xmax,ymax))
   #want fullscreen? pygame.display.set_mode((xmax,ymax), pygame.FULLSCREEN)
   white = (255, 255, 255)
   black = (0,0,0)

   particles = []
   for i in range(20):
       if i % 2 > 0: col = white
       else: col = (255,255,0)
#       particles.append( Particle(random.randint(1, xmax-1), random.randint(1, ymax-1), 0, 0, col) )
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
           
       pygame.display.flip()

   # Close the Pygame window
   pygame.quit()

#Run the system

if __name__ == "__main__":
    main()
