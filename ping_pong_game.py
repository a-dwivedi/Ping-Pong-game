import pygame
import random 

FPS = 70

#Dimensions of the rackets and the ball have been defined
RACKET_WIDTH = 20
RACKET_HEIGHT = 70 
BALL_WIDTH = 13
BALL_HEIGHT = 13
RACKET_SPEED = 8 
BALL_X_SPEED = 4
BALL_Y_SPEED = 3
GROUND_WIDTH = 350
GROUND_HEIGHT = 350
RACKET_BUFFER = 15
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

#initializing our game window by using the variables of ground's width and height described above
screen = pygame.display.set_mode((GROUND_WIDTH, GROUND_HEIGHT))
pygame.display.set_caption("Ping pong game")

#racket 1 is the agent which is learning by the reinforcement learning
#racket 2 is the trained model 
def racketDesign2(racket2_YPos):
    racket2 = pygame.Rect(GROUND_WIDTH - RACKET_BUFFER - RACKET_WIDTH, racket2_YPos, RACKET_WIDTH, RACKET_HEIGHT)
    pygame.draw.rect(screen, WHITE, racket2)
def racketDesign1(racket1_YPos):
    racket1 = pygame.Rect(RACKET_BUFFER, racket1_YPos, RACKET_WIDTH, RACKET_HEIGHT)
    pygame.draw.rect(screen, WHITE, racket1)
def ballDesign(ball_XAxis, ball_YAxis):
    ball = pygame.Rect(ball_XAxis, ball_YAxis, BALL_WIDTH, BALL_HEIGHT)
    pygame.draw.rect(screen, WHITE, ball)

#updating the positions of the rackets and the ba;;
def racket1Upgradation(action, racket1_YPos):
    if (action[1] == 1):
        racket1_YPos = racket1_YPos - RACKET_SPEED
    if (action[2] == 1):
        racket1_YPos = racket1_YPos + RACKET_SPEED
    if (racket1_YPos < 0):
        racket1_YPos = 0
    if (racket1_YPos > GROUND_HEIGHT - RACKET_HEIGHT):
        racket1_YPos = GROUND_HEIGHT - RACKET_HEIGHT
    return racket1_YPos

def racket2Upgradation(racket2_YPos, ball_Yaxis_Pos):
    if (racket2_YPos + RACKET_HEIGHT/2 < ball_Yaxis_Pos + BALL_HEIGHT/2):
        racket2_YPos = racket2_YPos + RACKET_SPEED
    if (racket2_YPos + RACKET_HEIGHT/2 > ball_Yaxis_Pos + BALL_HEIGHT/2):
        racket2_YPos = racket2_YPos - RACKET_SPEED
    if (racket2_YPos < 0):
        racket2_YPos = 0
    if (racket2_YPos > GROUND_HEIGHT - RACKET_HEIGHT):
        racket2_YPos = GROUND_HEIGHT - RACKET_HEIGHT
    return racket2_YPos
    
def ballUpgradation(racket1_YPos, racket2_YPos, ball_XaxisPos, ball_Yaxis_Pos, ball_X_Dir, ball_Y_Dir):
    ball_XaxisPos = ball_XaxisPos + ball_X_Dir * BALL_X_SPEED
    ball_Yaxis_Pos = ball_Yaxis_Pos + ball_Y_Dir * BALL_Y_SPEED
    score = 0
    if (
        ball_XaxisPos <= RACKET_BUFFER + RACKET_WIDTH  and ball_Yaxis_Pos + BALL_HEIGHT >= racket1_YPos and ball_Yaxis_Pos - BALL_HEIGHT <= racket1_YPos + RACKET_HEIGHT):
        ball_X_Dir = 1
    elif (ball_XaxisPos <= 0):
        ball_X_Dir = 1
        score = -1 
        return [score, racket1_YPos, racket2_YPos, ball_XaxisPos, ball_Yaxis_Pos, ball_X_Dir, ball_Y_Dir]
    if (
        ball_XaxisPos >= GROUND_WIDTH - RACKET_WIDTH - RACKET_BUFFER and ball_Yaxis_Pos + BALL_HEIGHT >= racket2_YPos and ball_Yaxis_Pos - BALL_HEIGHT <= racket2_YPos + RACKET_HEIGHT):
        ball_X_Dir = -1
    elif (ball_XaxisPos >= GROUND_WIDTH - BALL_WIDTH):
        ball_X_Dir = -1
        score = 1
        return [score, racket1_YPos, racket2_YPos, ball_XaxisPos, ball_Yaxis_Pos, ball_X_Dir, ball_Y_Dir]
    if (ball_Yaxis_Pos <= 0):
        ball_Yaxis_Pos = 0;
        ball_Y_Dir = 1;
    elif (ball_Yaxis_Pos >= GROUND_HEIGHT - BALL_HEIGHT):
        ball_Yaxis_Pos = GROUND_HEIGHT - BALL_HEIGHT
        ball_Y_Dir = -1
    return [score, racket1_YPos, racket2_YPos, ball_XaxisPos, ball_Yaxis_Pos, ball_X_Dir, ball_Y_Dir]

#ping pong game class defined
class PingPongGame:
    def __init__(self):
        num = random.randint(0,9)
        self.tally = 0
        self.racket1_YPos = GROUND_HEIGHT / 2 - RACKET_HEIGHT / 2
        self.racket2_YPos = GROUND_HEIGHT / 2 - RACKET_HEIGHT / 2
        self.ball_X_Dir = 1
        self.ball_Y_Dir = 1
        self.ball_XaxisPos = GROUND_WIDTH/2 - BALL_WIDTH/2
        if(0 < num < 3):
            self.ball_X_Dir = 1
            self.ball_Y_Dir = 1
        if (3 <= num < 5):
            self.ball_X_Dir = -1
            self.ball_Y_Dir = 1
        if (5 <= num < 8):
            self.ball_X_Dir = 1
            self.ball_Y_Dir = -1
        if (8 <= num < 10):
            self.ball_X_Dir = -1
            self.ball_Y_Dir = -1
        num = random.randint(0,9)
        self.ball_Yaxis_Pos = num*(GROUND_HEIGHT - BALL_HEIGHT)/9

    def capturePresentWindow(self):
        pygame.event.pump()
        screen.fill(BLACK)
        racketDesign1(self.racket1_YPos)
        racketDesign2(self.racket2_YPos)
        ballDesign(self.ball_XaxisPos, self.ball_Yaxis_Pos)
        captured_pixel_data = pygame.surfarray.array3d(pygame.display.get_surface())
        pygame.display.flip()
        return captured_pixel_data

    def captureNextWindow(self, action):
        pygame.event.pump()
        score = 0
        screen.fill(BLACK)
        self.racket1_YPos = racket1Upgradation(action, self.racket1_YPos)
        racketDesign1(self.racket1_YPos)
        self.racket2_YPos = racket2Upgradation(self.racket2_YPos, self.ball_Yaxis_Pos)
        racketDesign2(self.racket2_YPos)
        [score, self.racket1_YPos, self.racket2_YPos, self.ball_XaxisPos, self.ball_Yaxis_Pos, self.ball_X_Dir, self.ball_Y_Dir] = ballUpgradation(self.racket1_YPos, self.racket2_YPos, self.ball_XaxisPos, self.ball_Yaxis_Pos, self.ball_X_Dir, self.ball_Y_Dir)
        ballDesign(self.ball_XaxisPos, self.ball_Yaxis_Pos)
        captured_pixel_data = pygame.surfarray.array3d(pygame.display.get_surface())
        pygame.display.flip()
        self.tally = self.tally + score
        print ("Tally is" + str(self.tally))
        return [score, captured_pixel_data]
        
        #Display scores:
        font = pygame.font.Font(None, 74)
        text = font.render(str(score), 1, WHITE)
        screen.blit(text, (250,10))
        text = font.render(str(score), 1, WHITE)
        screen.blit(text, (420,10))

        pygame.display.flip()
        clock.tick(60)
