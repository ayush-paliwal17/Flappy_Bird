import pygame
from pygame.locals import *
import random
import sys, json

#Initialize all Pygame Modules
pygame.init()

#Global Variables
FPS = 32
FPSLOCK = pygame.time.Clock()
SCREENWIDTH, SCREENHEIGHT = 289 , 511
SCREEN = pygame.display.set_mode((SCREENWIDTH , SCREENHEIGHT))
pygame.display.set_caption("Flappy Bird by Ayush Paliwal")
GAME_SPRITES = {}
GAME_SOUNDS = {}
GROUNDY = SCREENHEIGHT * 0.8

#Game Sprites
PIPE = 'gallery/sprites/pipe.png'
GAME_SPRITES['numbers'] = (
    pygame.image.load('gallery/sprites/0.png').convert_alpha(),
    pygame.image.load('gallery/sprites/1.png').convert_alpha(),
    pygame.image.load('gallery/sprites/2.png').convert_alpha(),
    pygame.image.load('gallery/sprites/3.png').convert_alpha(),
    pygame.image.load('gallery/sprites/4.png').convert_alpha(),
    pygame.image.load('gallery/sprites/5.png').convert_alpha(),
    pygame.image.load('gallery/sprites/6.png').convert_alpha(),
    pygame.image.load('gallery/sprites/7.png').convert_alpha(),
    pygame.image.load('gallery/sprites/8.png').convert_alpha(),
    pygame.image.load('gallery/sprites/9.png').convert_alpha()
)
GAME_SPRITES['background'] = pygame.image.load('gallery/sprites/background.png').convert_alpha()
GAME_SPRITES['message'] = pygame.image.load('gallery/sprites/message.png').convert_alpha()
GAME_SPRITES['base'] = pygame.image.load('gallery/sprites/base.png').convert_alpha()
GAME_SPRITES['player'] = pygame.image.load('gallery/sprites/bird.png').convert_alpha()
GAME_SPRITES['pipe'] = (pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(),180),
                        pygame.image.load(PIPE).convert_alpha())

#Game Sounds
GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')
GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')
GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('gallery/audio/swoosh.wav')
GAME_SOUNDS['wing'] = pygame.mixer.Sound('gallery/audio/wing.wav')

#Dimentions
PIPEHEIGHT = GAME_SPRITES['pipe'][0].get_height()
PIPEWIDTH = GAME_SPRITES['pipe'][0].get_width()
PLAYERHEIGHT = GAME_SPRITES['player'].get_height()
PLAYERWIDTH = GAME_SPRITES['player'].get_width()

def highScore(score):

    with open('highscore.json') as f:
        check = json.load(f)

    if check['Score'] <= score:
        print("You have Created a new High Score")
        highScore = {"Score" : score}

        with open('highscore.json','w') as f:
            json.dump(highScore,f)

def randomPipes(pipeGap):
    """
    Returns Random y-axis positions of two pipes for blitting on screen.
    """
    offset = 180 #Minimum distance from origin for lower pipe

    yL = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height()  - 1.2 *offset))
    yU = PIPEHEIGHT - yL + pipeGap #The Gap between pipes will be reduced after every iteration to increase difficulty

    pipe = [
        {'x' : SCREENWIDTH + 10, 'yU' : -yU}, #upper pipe
        {'x' : SCREENWIDTH + 10, 'yL' : yL}, #lower pipe
    ]

    return pipe


def collisionCheck(playerx, playery, upperPipes, lowerPipes):
    """
    Checks if the bird has collided with the ground or any of the pipes.
    Returns true if bird collides.
    """
    check = False
    if playery >= GROUNDY - PLAYERHEIGHT:
        GAME_SOUNDS['hit'].play()
        check = True

    for pipe in lowerPipes:
        if playery > pipe['yL'] - PLAYERHEIGHT and pipe['x'] + PIPEWIDTH >= playerx >= pipe['x'] - PLAYERWIDTH:
            GAME_SOUNDS['hit'].play()
            check = True

    for pipe in upperPipes:
        if playery < pipe['yU'] + PIPEHEIGHT and pipe['x'] + PIPEWIDTH >= playerx >= pipe['x'] - PLAYERWIDTH:
            GAME_SOUNDS['hit'].play()
            check = True

    if check:
        return True

def welcomeScreen():
    """
    Greet the Player with a Welcome Screen.
    Calls the mainGame() or exits the game depending on the user input.
    """
    run = True
    while run:
        for event in pygame.event.get():
            #Quit the game on pressing Escape or 'cross' button.
            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE ):
                run = False
            #Start the game if Space key is pressed.
            elif event.type == KEYDOWN and event.key == K_SPACE:
                return
            else:
                SCREEN.blit(GAME_SPRITES['background'],(0,0))
                SCREEN.blit(GAME_SPRITES['player'],(121,270))
                SCREEN.blit(GAME_SPRITES['message'],(47,511*0.13))
                SCREEN.blit(GAME_SPRITES['base'],(0,GROUNDY))
                pygame.display.update()
    pygame.quit()
    sys.exit()


def mainGame():
    score = 0
    playerx = int(SCREENWIDTH/5)
    playery = (SCREENHEIGHT/2)
    pipeGap = 150

    #Generating 2 set of pipes for blitting
    pipe1 = randomPipes(pipeGap)
    pipe2 = randomPipes(pipeGap)

    #List of Upper pipes
    upperPipes = [
        {'x' : SCREENWIDTH+200, 'yU' : pipe1[0].get('yU')},
        {'x' : SCREENWIDTH+200+(SCREENWIDTH/2), 'yU' : pipe2[0].get('yU')  }
    ]

    #List of Lower pipes
    lowerPipes = [
        {'x' : SCREENWIDTH+200, 'yL' : pipe1[1].get('yL')},
        {'x' : SCREENWIDTH+200+(SCREENWIDTH/2), 'yL' : pipe2[1].get('yL')  }
    ]

    pipeVelX = -4 #speed at which pipes will move to the left

    playerVelY = -8 #Initial speed of fall
    playerMaxVelY = 10
    gravity = 1 #acceleration at which the bird will fall towards the ground i.e. gravity

    Flap = -8 #Flap velocity i.e. units flaped by bird
    playerFlapped = False #It will be true when the bird flaps

    #Bird Movements
    run = True
    while run:
        for event in pygame.event.get():
            #Quit the game on pressing Escape or 'cross' button.
            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                run = False
            #Flap the bird if Spacebar is pressed
            if event.type == KEYDOWN and (event.key == K_SPACE):
                if playery > 0: # So the player does not go above the origin.
                    playerVelY = Flap
                    playerFlapped = True
                    GAME_SOUNDS['wing'].play()

        if collisionCheck(playerx, playery, upperPipes, lowerPipes):
            print(f"Your Score is {score}")
            highScore(score)
            return

        #Droping the bird if no key is pressed
        if playerVelY < playerMaxVelY and not playerFlapped:
           playerVelY += gravity

        if playerFlapped:
            playerFlapped = False
        
        playery = min((playery + playerVelY), (GROUNDY - PLAYERHEIGHT))

        #move pipes to the left
        for upperPipe, lowerPipe in zip(upperPipes,lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX
        
        #add new pipe when the 1st is about to cross origin
        if 0 <upperPipes[0]['x']<4: # 4  because each iteration is moving the pipes by 4 units, so only one pipe will be produced for each iteration.
            newPipe = randomPipes(pipeGap)
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1]) 

        # if the pipe is out of the screen, remove it
        if upperPipes[0]['x'] < -PIPEWIDTH:
            upperPipes.pop(0)
            lowerPipes.pop(0)

        #Getting Score
        playerMid = playerx +PLAYERWIDTH/2
        pipeMid = upperPipes[0]['x'] + PIPEWIDTH/2
        if pipeMid <= playerMid < pipeMid + 4: # Because each iteration is taking 4 units of x axis, pipeMid +4 will ensure this condition is true only once per iteration.
            score+=1
            pipeGap -= 0.50
            GAME_SOUNDS['point'].play()
        
        #Screen Bliting
        SCREEN.blit(GAME_SPRITES['background'],(0,0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0],(upperPipe['x'],upperPipe['yU']))
            SCREEN.blit(GAME_SPRITES['pipe'][1],(lowerPipe['x'],lowerPipe['yL']))
        SCREEN.blit(GAME_SPRITES['player'],(playerx,playery))
        SCREEN.blit(GAME_SPRITES['base'],(0,GROUNDY))

        #Getting Width of entire Score
        scoreWidth = 0
        for digit in str(score):
            scoreWidth +=  GAME_SPRITES['numbers'][int(digit)].get_width() # this will generate the width of the entire score e.g. width of score = 25
        xoffset = (SCREENWIDTH - scoreWidth)/2

        #Score Bliting
        for digit in str(score):
            SCREEN.blit(GAME_SPRITES['numbers'][int(digit)],(xoffset,20))
            xoffset +=  GAME_SPRITES['numbers'][int(digit)].get_width()

        pygame.display.update()
        FPSLOCK.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    while True:
        welcomeScreen() # Shows Welcome Screen
        mainGame() # Main logic of the game

