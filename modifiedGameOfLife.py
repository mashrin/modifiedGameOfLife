import pygame
from pygame.locals import *
import sys
import random

pygame.init()

class Cell(pygame.sprite.Sprite):
    def __init__(self, game, pos, num):
        
        pygame.sprite.Sprite.__init__(self)
        
        self.age=1
        self.game = game
        self.gen=0
        self.quality=0
        self.num = num
        self.color=self.getColor()
        self.parent = 0
        self.unavailable=0
        
        self.image = pygame.Surface([10,10])
        self.image.fill((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        
        self.alive = False
        self.edge = False

        self.a_neighbors = []
        self.d_neighbors = []
        self.qualitylist=[0,0,0,0,0]

        self.n = (num - 74) - 1
        self.e = (num + 1) - 1
        self.s = (num + 74) - 1
        self.w = (num - 1) - 1
        self.ne = (self.n + 1)
        self.se = (self.s + 1)
        self.nw = (self.n - 1)
        self.sw = (self.s - 1)

        self.cell_list = [
            self.n,
            self.e,
            self.s,
            self.w,
            self.ne,
            self.se,
            self.nw,
            self.sw]

        self.game.cells.append(self)
        self.d={}
        
    def getColor(self):
        if (self.age>0) and (self.age<=14):
            self.state="Child"
        elif (self.age>14) and (self.age<=60):
            self.state="Adult"
        elif (self.age>60) and (self.age<=75):
            self.state="Elder"
        elif (self.age>75) and (self.age<=100):
            self.state="Elder2"
        if self.gen==0:
            if self.state=="Child":
                r,g,b=135,206,250
            elif self.state=="Adult":
                r,g,b=65,105,225
            elif self.state in ["Elder","Elder2"]:
                r,g,b=25,25,112
        elif self.gen==1:
            if self.state=="Child":
                r,g,b=255,182,193
            elif self.state=="Adult":
                r,g,b=255,20,147
            elif self.state in ["Elder","Elder2"]:
                r,g,b=176,48,96
        else:
            r,g,b=0,0,0
        return (r,g,b)
    
    def underdie(self):
        if self.state in ["Child","Elder","Elder2"]:
            if len(self.a_neighbors)==2:
                a=([True]*8)+([False]*2)
                b=random.choice(a)
                if b==True:
                    self.die()
                else:
                    self.survive()
            elif len(self.a_neighbors)==1:
                a=([True]*9)+([False]*1)
                b=random.choice(a)
                if b==True:
                    self.die()
                else:
                    self.survive()
            elif len(self.a_neighbors)==0:
                    self.die()
        elif self.state=="Adult":
            self.die()
        self.scaleQuality()
            
    def overdie(self):
        if self.state in ["Child","Elder","Elder2"]:
            if len(self.a_neighbors)==6:
                a=([True]*8)+([False]*2)
                b=random.choice(a)
                if b==True:
                    self.die()
                else:
                    self.survive()
            elif len(self.a_neighbors)==7:
                a=([True]*9)+([False]*1)
                b=random.choice(a)
                if b==True:
                    self.die()
                else:
                    self.survive()
            elif len(self.a_neighbors)==8:
                    self.die()
        elif self.state=="Adult":
            self.die()
        self.scaleQuality()
            
    def die(self):
        self.alive = False
        for i in self.a_neighbors:
            i.quality-=1
        self.unavailable=self.game.generation
        self.qualitylist=[]
        self.scaleQuality()

    def survive(self):
        if self.state=="Child":
            if self.age in range(0,6):
                if [1,"Adult"] in self.d.values():
                    self.age+=1
                else:
                    self.die()
            elif self.age in range(6,11):
                if [1 or 0,"Adult"] in self.d.values():
                    self.age+=1
                else:
                    self.die()
            else:
                self.age+=1
        elif self.state=="Adult":
            self.age+=1
        elif self.state=="Elder":
            self.age+=1
        elif self.state=="Elder2":
            a=([True]*(100-4*(self.age-75)))+([False]*(4*(self.age-75)))
            b=random.choice(a)
            if b==False:
                self.die()
            else:
                self.quality-=0.1
                self.age+=1
        self.scaleQuality()
        
    def scaleQuality(self):
        if self.quality>=100:
            self.quality=100
        if self.quality<=0:
            self.quality=0
            
    def born(self):
        if (self.game.generation>=self.unavailable+5) or ((self.game.generation in [0,1,2,3,4,5])and (self.unavailable==0)):
            self.alive=True
            self.gen=random.randint(0,1)
            self.quality=100
            for i in self.a_neighbors:
                if i.state=="Adult":
                    i.quality+=3
                elif i.state in ["Elder","Elder2"]:
                    i.quality+=2.5
            self.scaleQuality()
            
    def setQuality(self):
        if self.state=="Child":
            if ([0,"Elder"] not in self.d.values())or ([1,"Elder"] not in self.d.values()) or ([0,"Elder2"] not in self.d.values()) or ([1,"Elder2"] not in self.d.values()):
                self.quality-=0.2
            if ([1,"Adult"] not in self.d.values()) and ([0,"Adult"] in self.d.values()):
                self.quality-=1
            elif ([0,"Adult"] not in self.d.values())and ([1,"Adult"] not in self.d.values()):
                self.quality-=1.5
            
        elif self.state=="Adult":
            if ([0,"Elder"] not in self.d.values())or ([1,"Elder"] not in self.d.values()) or ([0,"Elder2"] not in self.d.values()) or ([1,"Elder2"] not in self.d.values()):
                self.quality-=0.2
        if self.age==15:
            self.quality-=0.5
        if self.age==61:
            self.quality-=0.5
        self.scaleQuality()
         
    def update(self):
        if not self.edge:
            self.a_neighbors = []
            self.d_neighbors = []
            self.neighbors = [self.game.cells[cell] for cell in self.cell_list]

            for n in self.neighbors:
                if n.alive:
                    self.a_neighbors.append(n)
                else:
                    self.d_neighbors.append(n)   
            self.d={i:[i.gen,i.state] for i in self.a_neighbors}
            if not self.game.running:
                    
                if pygame.mouse.get_pressed()[0] and self.rect.collidepoint(self.game.mpos):
                    self.gen=0
                    self.age=self.game.age
                    if self.age==1:
                        self.quality=100
                    elif self.age==15:
                        self.quality=80
                    elif self.age==61:
                        self.quality=60
                    self.alive = True
                    
                if pygame.mouse.get_pressed()[2] and self.rect.collidepoint(self.game.mpos):
                    self.gen=1
                    self.age=self.game.age
                    if self.age==1:
                        self.quality=100
                    elif self.age==15:
                        self.quality=80
                    elif self.age==61:
                        self.quality=60
                    self.alive = True
                    
                if self.rect.collidepoint(self.game.mpos):
                    self.game.quality=self.quality
                    
                if self.alive:
                    self.image.fill(self.getColor())
            else:
                if self.alive:
                    self.image.fill(self.getColor())
                    
                if not self.alive:
                    self.age=1
                    self.quality=0
                    self.image.fill((0, 0, 0))
                    
                if self.rect.collidepoint(self.game.mpos):
                    self.game.quality=self.quality
                    
        else:
            self.image.fill((255, 255, 255))
        self.scaleQuality()

            


class Game():
    def __init__(self):
        #window setup
        pygame.display.set_caption('Game Of Life')
        
        # initiate the clock and screen
        self.clock = pygame.time.Clock()
        self.last_tick = pygame.time.get_ticks()
        self.screen_res = [740, 540]
        self.quality=0
        self.age=15
        self.font = pygame.font.SysFont("Times New Roman", 19)

        self.sprites = pygame.sprite.Group()
        self.cells = []
        self.generation = 0
        self.population = 0
        self.screen = pygame.display.set_mode(self.screen_res, pygame.HWSURFACE, 32)

        self.running = False
        self.createGrid()
        self.poplist=[0,0,0,0,0]
     
        while 1:
            self.Loop()

    def createGrid(self):
        col = 0
        row = 50
        cell_num = 0

        for y in xrange(44):
            for x in xrange(74):
                cell_num +=1
                cell = Cell(self, [col, row], cell_num)
                if row == 50 or row  == 480 or col == 0 or col == 730:
                    cell.edge = True
                self.sprites.add(cell)
                col += 10
            row += 10
            col = 0
          
    def Run(self):
        self.population = 0
        for cell in self.cells:
            if cell.alive:
                self.population += 1
                if len(cell.a_neighbors) in [3,4,5]:
                    cell.survive()
                elif (len(cell.a_neighbors) < 3):
                    cell.underdie()
                elif (len(cell.a_neighbors)>5):
                    cell.overdie()
                if cell.age>=100:
                    cell.die()
                cell.setQuality()
            else:
                if (len(cell.a_neighbors) == 3):
                    z=False
                    for i in cell.a_neighbors:
                        if cell.d[i]==[0,"Adult"]:
                            for j in i.a_neighbors:
                                if (i.d[j]==[1,"Adult"]) and (j in cell.a_neighbors):
                                    z=True
                        elif cell.d[i]==[1,"Adult"]:
                            for j in i.a_neighbors:
                                if (i.d[j]==[0,"Adult"]) and (j in cell.a_neighbors):
                                    z=True
                    if z==True:
                        cell.born()
        if (self.population==self.poplist[-2]==self.poplist[-3]==self.poplist[-4]==self.poplist[-5]) and (self.population!=0):
            count=0
            while count!=5:
                a=random.choice(self.cells)
                if a.alive==False:
                    count1=0
                    a.born()
                    a.age=15
                    a.quality=80
                    if len(a.d_neighbors)>=5:
                        z=random.randint(2,5)
                    elif len(a.d_neighbors)>2:
                        z=random.randint(2,len(a.d_neighbors))
                    elif len(a.d_neighbors)<=2:
                        z=len(a.d_neighbors)
                    while count1!=z:
                        b=random.choice(a.d_neighbors)
                        b.born()
                        b.age=15
                        b.quality=80
                        count1+=1
                    count+=1
        for cell in self.cells:
            if cell.alive:
                cell.qualitylist.append(cell.quality)
                if(cell.quality==cell.qualitylist[-5]==cell.qualitylist[-4]==cell.qualitylist[-3]==cell.qualitylist[-2]==0):
                    cell.die()
            else:
                cell.qualitylist=[0,0,0,0,0]
                

                    
    def blitDirections(self):
        text = self.font.render("Enter = Next Gen, R-click = Female, L-click = Male, and R to Reset", 1, (255,255,255))
        generations = self.font.render("Generation: %s" %str(self.generation), 1, (255,255,255))
        pop = self.font.render("Pop: %s" %str(self.population), 1, (255,255,255))
        qual=self.font.render("Quality: %s" %str(self.quality),1,(255,255,255))
        self.screen.blit(text, (100, 15))
        self.screen.blit(generations, (10, 500))
        self.screen.blit(pop, (650, 500))
        self.screen.blit(qual,(325,500))

    def Loop(self):
        # main game loop
        self.eventLoop()
        
        self.Tick()
        self.Draw()
        pygame.display.update()

    def eventLoop(self):
        # the main event loop, detects keypresses
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    self.running = True
                    self.next=True
                if event.key == K_SPACE:
                    self.running = False
                if event.key == K_r:
                    self.running=False
                    self.sprites.empty()
                    self.cells=[]
                    self.createGrid()
                    self.generation=0
                    self.population=0
                    self.poplist=[0,0,0,0,0]
                    self.age=15
                if event.key == K_a:
                    self.age=15
                if event.key == K_e:
                    self.age=61
                if event.key == K_c:
                    self.age=1



    def Tick(self):
        # updates to player location and animation frame
        self.ttime = self.clock.tick()
        self.mpos = pygame.mouse.get_pos()
        self.keys_pressed = pygame.key.get_pressed()
        if self.running and self.next:
            #self.next=False
            self.poplist.append(self.population)
            print(self.poplist,self.population)
            #pygame.time.wait(100)
            self.generation +=1
            self.Run()


    def Draw(self):
        self.screen.fill(0)
        self.blitDirections()
        self.sprites.update()
        self.sprites.draw(self.screen)

Game()
