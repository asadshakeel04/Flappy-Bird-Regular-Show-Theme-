import pygame
from pygame.locals import *
import random

pygame.init()

'''GAME VARIABLES'''

#Game speed
time = pygame.time.Clock()
fps = 60

#Variables used for screen dimensions
height = 600
width = 500

#Variables used for moving ground
scroll = 0
move = 3

#Variables used for start and end of game
start = False
end = False

#Variables used for pipes
gap = 150
frequency = 1500
pipe_time = pygame.time.get_ticks() - frequency

#Variables used for score
passed_pipes = []
score = 0
font = pygame.font.SysFont('Bauhaus 93', 60)
font2 = pygame.font.SysFont("Arial Rounded MT Bold", 60)
white = (255, 255, 255)
gold = (255, 215, 0)
high_score = 0

#Variables used for in game features
powerup_time = 0
vgame = pygame.image.load('vgame.png')
rigby = pygame.image.load('rigby.png')

#Loading images
background = pygame.image.load('flappybirdbackground.png')
ground = pygame.image.load('flappybirdground.png')
restart_button = pygame.image.load('restart.png')

#Setting screen
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Flappy Bird")

#Show score on screen
def scorecard(text, font, color, x, y):
    image = font.render(text, True, color)
    screen.blit(image, (x, y))

#Reset game if restart is pressed
def reset():
    pipes.empty()
    flappy.rect.x = 100
    flappy.rect.y = height//2
    score = 0
    return score

#Creating bird
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        self.low = 0
        self.clicked = False
        self.jump = -7

        #Load and store all bird images
        for i in range(1, 4):
            img = pygame.image.load(f'mordecai{i}.png')
            img = pygame.transform.scale(img, (55, 55))

            self.images.append(img)

        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    #Function used for bird to be animated/moving
    def animation(self):

        #When game starts, bird is falling down automatically
        if start == True:
            self.low += 0.5
            if self.low > 10:
                self.low = 10
            if self.rect.bottom < 500:
                self.rect.y += int(self.low)
        
        #Before game ends, bird can jump if mouse is pressed or spacebar is pressed
        if end == False:
            #Mouse
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.low = self.jump
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
            
            #Spacebar
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.clicked == False:
                self.clicked = True
                self.low = self.jump
            if not key[pygame.K_SPACE]:
                self.clicked = False
                
            self.counter += 1
            animation_time = 5

            #Animation time determines how long before the bird changes
            if self.counter > animation_time:
                self.counter = 0
                self.index += 1

                #Make sure index is within range
                self.index %= 3
            
            self.image = self.images[self.index]

            #Bird rotates as it jumps for more animation
            self.image = pygame.transform.rotate(self.images[self.index], self.low * -2)
        else:
            #When bird hits the ground, it will rotate sideways to show game is over
            self.image = pygame.transform.rotate(self.images[self.index], -90)

#Creating pipes
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, z):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('pipe.png')
        self.rect = self.image.get_rect()
        #z will either be 1 for top pipe or -1 for bottom pipe
        if z == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - gap//2]
        if z == -1:
            self.rect.topleft = [x, y + gap//2]   
    
    #Pipe scrolls at same rate as ground
    def animation(self):
        self.rect.x -= move
        #When pipe is off screen, delete
        if self.rect.right == 0:
            self.kill() 

#Restart button
class Restart():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    #Show restart button and check if pressed
    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                return True
        #returns False if not pressed, True if pressed
        return False

#Creating Powerups
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, img, type):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(img, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.type = type
    
    #Save memory by killing image if passed by bird
    def update(self):
        self.rect.x -= move
        if self.rect.right < 0:
            self.kill()

birds = pygame.sprite.Group()
flappy = Bird(100, height//2)
birds.add(flappy)

pipes = pygame.sprite.Group()

restart = Restart(width // 2 - 50, height // 2 - 75, restart_button)

powerups = pygame.sprite.Group()

'''RUNNING GAME'''
while True:
    
    #Game speed
    time.tick(fps)

    #Show images
    screen.blit(background, (0,0))
    screen.blit(ground, (scroll, 500))

    #Show bird
    birds.draw(screen)
    for bird in birds:
        bird.animation()
    
    #Show pipes
    pipes.draw(screen)

    #If bird hits ground, game is over
    if flappy.rect.bottom > 500:
        start = False
        end = True

    #Update score
    for pipe in pipes:
        #When bird is between a pipe
        if flappy.rect.left > pipe.rect.left and flappy.rect.right < pipe.rect.right and pipe not in passed_pipes:
            passed_pipes.append(pipe)
            #Since there is a top and bottom pipe, we use this check so it only increments one to score
            if len(passed_pipes) % 2 == 0:
                score += 1
    
    scorecard(str(score), font, white, width//2 - 10, 20)


    #If bird collides with pipe, game is over
    if pygame.sprite.groupcollide(birds, pipes, False, False) or flappy.rect.top < 0:
        end = True

    #If game is still active
    if end == False and start == True:
        #Pipes will show at random heights at a certain frequency
        current = pygame.time.get_ticks()
        if current - pipe_time > frequency:
            random_height = random.randint(-100, 100)
            bottom = Pipe(width, height//2 + random_height, -1)
            top = Pipe(width, height//2 + random_height, 1)
            pipes.add(bottom)
            pipes.add(top)
            pipe_time = current

            #There is a 5% chance a videogame powerup spawns
            if random.randint(1, 20) == 1:
                powerup = PowerUp(width - 50, height//2 + random_height, vgame, 'vgame')
                powerups.add(powerup)
            
            #There is a 1% chance a rigby powerup spawns
            elif random.randint(1, 100) == 1:
                powerup = PowerUp(width - 50, height//2 + random_height, rigby, 'rigby')
                powerups.add(powerup)

        #Ground only scrolls when game is still active
        scroll -= move
        if abs(scroll) > 25:
            scroll = 0

        #Pipes only show when game is still active
        for pipe in pipes:
            pipe.animation()
    
    #If bird hits videogame, the jump strength is reduced for 5 seconds
    #If bird hits rigby, score is increased by 10
    powerups.update()
    powerups.draw(screen)
    for powerup in pygame.sprite.spritecollide(flappy, powerups, True):
        if powerup.type == 'vgame':
            flappy.jump = -5
            powerup_time = pygame.time.get_ticks()
        elif powerup.type == 'rigby':
            score += 10
    
    if pygame.time.get_ticks() - powerup_time > 5000 or end == True:
        flappy.jump = -7
        powerup_time = 0
    
    #If game is over, show restart button
    if end == True:
        #Update high score if needed and show on screen
        if score > high_score:
            high_score = score
        scorecard("High Score: " + str(high_score), font2, gold, width//2 - 125, 150)
            
        #draw returns True if restart is pressed
        if restart.draw() == True:
            end = False
            #Reset function resets all variables and returns 0 for score
            score = reset()

    for event in pygame.event.get():
        #Exit game
        if event.type == pygame.QUIT:
            end = False
        #Start game
        if event.type == pygame.MOUSEBUTTONDOWN and start == False and end == False:
            start = True

    #Update screen
    pygame.display.update()

pygame.quit()