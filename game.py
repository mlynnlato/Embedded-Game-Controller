# Based on: https://youtu.be/aHmtOrrLmxg
import pygame, math, random, serial

##################################
# CHANGE THIS TO YOUR SERIAL PORT:
SERIAL_PORT = 'COM4'
##################################

pygame.init()

pygame.display.set_caption('Top Gun')

#Import asset images
background = pygame.image.load("assets/sky.jpg")
jet = pygame.image.load("assets/jet.png")
bomber = pygame.image.load("assets/bomber.png")
bullet = pygame.image.load("assets/bullet.png")
topgun = pygame.image.load("assets/topgun.png")
tomcruise = pygame.image.load("assets/tomcruise.jpg")
explode = pygame.image.load("assets/explode.png")
sadcruise = pygame.image.load("assets/sadcruise.jpg")
bgrect = background.get_rect()

#Initialize variables:
clock = pygame.time.Clock()
screen_width = 850
screen_height = 600
surface = pygame.display.set_mode((screen_width,screen_height))
green = 0,255,0
red = 255,0,0
blue = 0,0,255
yellow = 255,255,0
white = 255,255,255
black = 0,0,0

lives = 8
score = 0

bgOffset = -1 * bgrect.height

pygame.mixer.init()
try:
    pygame.mixer.music.load("assets/topguntheme.mp3")
    pygame.mixer.music.play(-1)
except:
    print("Unable to play audio")

try:
    explodeSf = pygame.mixer.Sound("assets/explode.mp3")
except:
    print("Unable to load audio file")

class Square:
    def __init__(self, color, x, y, width, height, image = None):
        self.rect = pygame.Rect(x,y,width,height)
        self.color = color
        self.direction = 'E'
        self.speed = 10
        self.image = image
        self.alive = True

    def move(self):
        if self.direction == 'E':
            self.rect.x = self.rect.x+self.speed
        if self.direction == 'W':
            self.rect.x = self.rect.x-self.speed
        if self.direction == 'N':
            self.rect.y = self.rect.y-self.speed
        if self.direction == 'S':
            self.rect.y = self.rect.y+self.speed

    def collided(self, other_rect):
        #Return True if self collided with other_rect
        return self.rect.colliderect(other_rect)

    def draw(self, surface):
        if self.image != None:
            if self.alive:
                surface.blit(self.image,self.rect)
            else:
                surface.blit(explode,self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)

 #Open COM port
ser = serial.Serial()
ser.baudrate = 9600
ser.port = SERIAL_PORT
try:
    ser.open()
except:
    print("Unable to open serial port")

#Build a square
sq_size = 100
sq = Square(green,350,400,sq_size,sq_size,jet)
sq.speed = 10

bullets = []
enemies = []

#Main program loop
done = False
intro = True
gameOver = False
shueNuke= False
useNuke=False
nukeMsg=False
nukePoints=0
nukeScore=0
while not done:
    #Get user input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            print(event.key) #Print value of key press
            if event.key==119: #w
                sq.direction = 'N'
                sq.move()
            if event.key==97: #a
                sq.direction = 'W'
                sq.move()
            if event.key==115: #s
                sq.direction = 'S'
                sq.move()
            if event.key==100: #d
                sq.direction = 'E'
                sq.move()
            if event.key==32 and shueNuke: #spacebar
                #Fire a bullet
                spawnx = sq.rect.x + sq.rect.width/2 - 10
                b = Square(red, spawnx,sq.rect.y, 20,20,bullet)
                b.direction = 'N'
                b.speed = 20
                bullets.append(b)

    #Read serial port
    if ser.isOpen():
        if ser.in_waiting > 0:
            input = int.from_bytes(ser.read(), "little")
            ser.flush()
            ser.flushInput()
            print(input) #Print value of key press
            if input==255 and shueNuke==False:
                #Fire a bullet
                bullet = pygame.image.load("assets/bullet.png")
                spawnx = sq.rect.x + sq.rect.width/2 - 10
                b = Square(red, spawnx,sq.rect.y, 20,20,bullet)
                b.direction = 'N'
                b.speed = 10
                bullets.append(b)
            elif input==255 and shueNuke==True:
                bullet = pygame.image.load("assets/shue.jpg")                
                spawnx = 0
                b = Square(red, spawnx,sq.rect.y, 20,20,bullet)
                b.direction = 'N'
                b.speed = 10
                bullets.append(b)
                shueNuke=False
                nukeMsg = True
                nukePoints=nukePoints+len(enemies)
                nukeScore=0
                score=len(enemies)+score
                enemies.clear()
                

            else:
                sq.rect.x = (input/254) * (screen_width - sq_size)

    # If on intro screen:
    if intro:
        surface.blit(tomcruise,(0,0))
        surface.blit(topgun,(25,400))
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render('Press Fire to Start', True, white)
        textRect = text.get_rect()
        textRect.center = ((screen_width/2), (375))
        surface.blit(text, textRect)
        pygame.display.flip()
        # if the shoot button has been pressed, leave intro screen
        if len(bullets) > 0:
            bullets.clear()
            intro = False
            try:
                pygame.mixer.music.load("assets/dangerzone.mp3")
                pygame.mixer.music.play(-1)
            except:
                print("Unable to play audio")
    elif gameOver:
        surface.blit(sadcruise,(0,0))
        font = pygame.font.Font('freesansbold.ttf', 75)
        text = font.render("Game Over", True, white)
        textRect = text.get_rect()
        textRect.center = ((screen_width/2), (300))
        surface.blit(text, textRect)
        text = font.render("Score: " + str(score), True, white)
        textRect = text.get_rect()
        textRect.center = ((screen_width/2), (400))
        surface.blit(text, textRect)
        pygame.display.flip()
        
    else:
        #Update game objects
        for b in bullets:
            b.move()
        for e in enemies:
            e.move()
        
        #spawn enemies on the top of the screen and tell them to move down
        if random.randint(1,30) == 15: #15 doesn't matter
            x = random.randint(0,screen_width-100)
            e = Square(yellow, x, -100, 100, 100, bomber)
            e.direction = 'S'
            enemies.append(e)
        #Check for collisions
        for j in reversed(range(len(enemies))):
            if enemies[j].alive:
                if enemies[j].collided(sq.rect):
                        # enemey hit player
                        sq.alive = False
                        enemies[j].alive = False
                        lives = lives - 1
                        if lives < 0:
                            lives = 0
                        try:
                            pygame.mixer.Sound.play(explodeSf)
                        except:
                            print("Unable to play audio")
                else:     
                    # check for bullets hitting enemies       
                    for i in reversed(range(len(bullets))):
                        if bullets[i].collided(enemies[j].rect):
                            enemies[j].alive = False
                            del bullets[i]
                            score = score + 1
                            nukeScore=nukeScore+1
                            try:
                                pygame.mixer.Sound.play(explodeSf)
                            except:
                                print("Unable to play audio")
                            break
            else:
                del enemies[j]


        # All the drawing
        surface.fill(black) #fill surface with black
        # fill surface with clouds 
        bgOffset = bgOffset + 5
        if bgOffset > 0:
            bgOffset = -1 * bgrect.height
        
        for y in range(0 + bgOffset,screen_height,bgrect.height):
            for x in range(0,screen_width,bgrect.width):
                surface.blit(background,(x,y))

        for b in bullets:
            b.draw(surface)
        for e in enemies:
            e.draw(surface)

        sq.draw(surface)
        if lives > 0:
            sq.alive = True
        else:
            try:
                pygame.mixer.music.load("assets/topguntheme.mp3")
                pygame.mixer.music.play(-1)
            except:
                print("Unable to play audio")
            gameOver = True

        

        # display health
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render("Lives: " + str(lives), True, black)
        surface.blit(text, (0,0))
        text = font.render("Score: " + str(score), True, black)
        surface.blit(text, (0,50))


        if nukeMsg:
            text= font.render("You dropped a SHUE NUKE! You earned " + str(nukePoints) + " extra points!", True, white)
            surface.blit(text, (0,150))

        if nukeScore > 4:
            text = font.render("SHUE NUKE AVALIABLE!", True, red)
            surface.blit(text, (0,100))
            shueNuke= True
        
        print("Nuke Score" + str(nukeScore))

        pygame.display.flip()
        clock.tick(30) #30 FPS
pygame.quit()
exit()
