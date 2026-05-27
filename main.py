import sys, pygame, math, random, asyncio

#Project started 9/22/2025
#initialize program
pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Project Beats Remix")

#GUI and related
size = width, height = 1280, 720
screen = pygame.display.set_mode(size)
fps = pygame.time.Clock()
player = pygame.rect.Rect(width/2-10, height/2-10, 20, 20)
#WIP
screenID = 1

#Music and related
activeMusic = None
busyFading = False
fading = True
fade_speed = 0.05
volume = 1.0
pygame.mixer.music.set_volume(volume)
musicFolder = 'Music/'
RectLobbyMusic = 'StartTheStars.ogg'
damageSFX = pygame.mixer.Sound('SFX/damageSFX.ogg')

#Text and related
font = pygame.font.Font(None, 40)
musicFont = pygame.font.Font('Font/NotoMusic-Regular.ttf', 40)

#Enemies and Logic
RectEnemies = []
ExplodeEnemies = []
LaserEnemies = []
GlideEnemies = []
SpinEnemies = []

#Other
debug = False
code = [pygame.K_d, pygame.K_e, pygame.K_b, pygame.K_u, pygame.K_g]
idx = 0
globalTimer = 0

def musicFontAnimation(globalTimer, interval, size):
    global musicFont
    if globalTimer%interval<interval/10:
        musicFont = pygame.font.Font('Font/NotoMusic-Regular.ttf', size+5)
    elif globalTimer%interval<interval/5:
        musicFont = pygame.font.Font('Font/NotoMusic-Regular.ttf', size-5)
    else:
        musicFont = pygame.font.Font('Font/NotoMusic-Regular.ttf', size)

def enemyLogic(LT):
    global RectEnemies
    global ExplodeEnemies
    global LaserEnemies
    global GlideEnemies
    global SpinEnemies

    i = len(LaserEnemies) - 1
    # [pygame.rect.Rect(x, y, w, h), LT, t, warn, False]
    while i > -1:
        if LaserEnemies[i][1] + LaserEnemies[i][2] == LT:
            LaserEnemies.pop(i)
            i -= 1
            continue
        elif LaserEnemies[i][1] - LaserEnemies[i][3] <= LT < LaserEnemies[i][1]:
            pygame.draw.rect(screen, "pink", LaserEnemies[i][0])
        elif LT >= LaserEnemies[i][1]:
            pygame.draw.rect(screen, "red", LaserEnemies[i][0])
            LaserEnemies[i][4] = True
        i -= 1

    i = len(GlideEnemies) - 1
    # [pygame.rect.Rect(x, y, w, h), pygame.rect.Rect(x2, y2, w, h), LT, dur, warn, vx, vy, t]
    while i > -1:
        if GlideEnemies[i][2] + GlideEnemies[i][3] == LT:
            GlideEnemies.pop(i)
            i -= 1
            continue
        elif GlideEnemies[i][2] - GlideEnemies[i][3] <= LT < GlideEnemies[i][2]:
            pygame.draw.rect(screen, "pink", GlideEnemies[i][0])
        elif GlideEnemies[i][2] <= LT < GlideEnemies[i][2] + GlideEnemies[i][7]:
            GlideEnemies[i][1] = moveObject(GlideEnemies[i][1], GlideEnemies[i][5], GlideEnemies[i][6])
        pygame.draw.rect(screen, "red", GlideEnemies[i][1])
        i -= 1
    i = len(SpinEnemies) - 1

    # [surface, cx, cy, vx, vy, a, da, LT, t, warn, False]
    while i > -1:
        if SpinEnemies[i][7] + SpinEnemies[i][8] == LT:
            SpinEnemies.pop(i)
            i -= 1
            continue
        elif SpinEnemies[i][7] - SpinEnemies[i][9] <= LT < SpinEnemies[i][7]:
            SpinEnemies[i][0].fill("pink")
        elif LT >= SpinEnemies[i][7]:
            SpinEnemies[i][0].fill("red")
            SpinEnemies[i][10] = True
        SpinEnemies[i][1] += SpinEnemies[i][3]
        SpinEnemies[i][2] += SpinEnemies[i][4]
        SpinEnemies[i][5] += SpinEnemies[i][6]

        # Rotate and draw
        rotated = pygame.transform.rotate(SpinEnemies[i][0], SpinEnemies[i][5])
        rotated_rect = rotated.get_rect(center=(SpinEnemies[i][1], SpinEnemies[i][2]))
        screen.blit(rotated, rotated_rect.topleft)
        i -= 1
    i = 0
    while i < len(RectEnemies):
        RectEnemies[i][0] = moveObject(RectEnemies[i][0], RectEnemies[i][1], RectEnemies[i][2])
        if (RectEnemies[i][0].x < 0 - RectEnemies[i][0].width and RectEnemies[i][1] < 0 or
                RectEnemies[i][0].x > 1280 and RectEnemies[i][1] > 0 or
                RectEnemies[i][0].y < 0 - RectEnemies[i][0].height and RectEnemies[i][2] < 0 or
                RectEnemies[i][0].y > 720 and RectEnemies[i][2] > 0):
            RectEnemies.pop(i)
            continue
        pygame.draw.rect(screen, "red", RectEnemies[i][0])
        i += 1
    i = 0
    while i < len(ExplodeEnemies):
        ExplodeEnemies[i][0] = moveObject(ExplodeEnemies[i][0], ExplodeEnemies[i][1], ExplodeEnemies[i][2])
        if ExplodeEnemies[i][3] == LT:
            for j in range(1, ExplodeEnemies[i][4][3] + 1):
                RectEnemies.append(generateBasic(ExplodeEnemies[i][0].centerx, ExplodeEnemies[i][0].centery,
                                                 ExplodeEnemies[i][4][0], ExplodeEnemies[i][4][1],
                                                 round(ExplodeEnemies[i][4][2] * math.cos(
                                                     2 * math.pi * j / ExplodeEnemies[i][4][3])),
                                                 round(ExplodeEnemies[i][4][2] * math.sin(
                                                     2 * math.pi * j / ExplodeEnemies[i][4][3]))))
            ExplodeEnemies.pop(i)
            continue
        pygame.draw.rect(screen, "orange", ExplodeEnemies[i][0])
        i += 1

#Screen 2
RectLevelMusic = [[pygame.rect.Rect(0*width/4, 0*height/3, width/4, height/3), 'CoconutMall.ogg'],
                  [pygame.rect.Rect(1*width/4, 0*height/3, width/4, height/3), 'Focus.ogg'],
                  [pygame.rect.Rect(2*width/4, 0*height/3, width/4, height/3), 'Chronos.ogg'],
                  [pygame.rect.Rect(3*width/4, 0*height/3, width/4, height/3), 'Sevcon.ogg'],

                  [pygame.rect.Rect(0*width/4, 1*height/3, width/4, height/3), 'MilkyWays.ogg'],
                  [pygame.rect.Rect(3*width/4, 1*height/3, width/4, height/3), 'Tetris.ogg'],

                  [pygame.rect.Rect(0*width/4, 2*height/3, width/4, height/3), 'StartTheStars.ogg'],
                  [pygame.rect.Rect(1*width/4, 2*height/3, width/4, height/3), 'StartTheStars.ogg'],
                  [pygame.rect.Rect(2*width/4, 2*height/3, width/4, height/3), 'StartTheStars.ogg'],
                  [pygame.rect.Rect(3*width/4, 2*height/3, width/4, height/3), 'StartTheStars.ogg'],]

#Global gravity
Gvx, Gvy = 0, 0

#Player speed
speed = 5

def drawText(font, text, color, x, y, alpha):
    surface = font.render(text, True, color).convert_alpha()
    surface.set_alpha(alpha)
    screen.blit(surface, (x, y))

def movePlayer(player):
    if Gvx > 0 and player.x < 1260 or Gvx < 0 and player.x > 0: player.x += Gvx
    if Gvy < 0 and player.y > 0 or Gvy > 0 and player.y < 700: player.y += Gvy
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]: player.y = max(0, player.y - speed)
    if keys[pygame.K_a] or keys[pygame.K_LEFT]: player.x = max(0, player.x - speed)
    if keys[pygame.K_s] or keys[pygame.K_DOWN]: player.y = min(700, player.y + speed)
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]: player.x = min(1260, player.x + speed)


def moveObject(rect, vx, vy):
    rect.x += vx
    rect.y += vy
    return rect

#Generates a basic enemy
def generateBasic(x, y, w, h, vx, vy):
    return [pygame.rect.Rect(x, y, w, h), vx, vy]

#Generates an enemy for a certain time
def generateLaser(x, y, w, h, LT, t, warn):
    return [pygame.rect.Rect(x, y, w, h), LT, t, warn, False]

def generateGliding(x, y, w, h, LT, dur, warn, x2, y2, vx, vy, t):
    return [pygame.rect.Rect(x, y, w, h), pygame.rect.Rect(x2, y2, w, h), LT, dur, warn, vx, vy, t]

#Generates an exploding enemy into n different enemies
def generateExploding(x, y, w, h, vx, vy, LT, ew, eh, ev, n):
    return [pygame.rect.Rect(x, y, w, h), vx, vy, LT, (ew, eh, ev, n)]

#Generates a spinning enemy
def generateSpinning(cx, cy, w, h, vx, vy, a, da, LT, t, warn):
    surface = pygame.Surface((w, h), pygame.SRCALPHA)
    return [surface, cx, cy, vx, vy, a, da, LT, t, warn, False]

def transitionColor(LT, time, diff, color1, color2):
    value1 = round(color1[0] + (color2[0]-color1[0])*((diff-(time-LT))/diff))
    value2 = round(color1[1] + (color2[1]-color1[1])*((diff-(time-LT))/diff))
    value3 = round(color1[2] + (color2[2]-color1[2])*((diff-(time-LT))/diff))
    screen.fill((value1, value2, value3))

#Level functions
def damageCheck(lives, INVT, LT):
    if lives == 0:
        player.centerx = width / 2
        player.centery = height / 2
        print("You died")
    elif INVT > LT:
        pygame.draw.circle(screen, "cyan", player.center, 18)
    if lives == 3:
        pygame.draw.rect(screen, "blue", player)
    elif lives == 2:
        pygame.draw.rect(screen, "yellow", player)
    elif lives == 1:
        pygame.draw.rect(screen, "dark red", player)

def invCheck(lives, INVT, LT, player_mask):
    # Handle invincibility
    if INVT <= LT:
        for i in RectEnemies:
            if player.colliderect(i[0]):
                damageSFX.play(0)
                lives -= 1
                INVT = LT + 120
                break
        for i in ExplodeEnemies:
            if player.colliderect(i[0]):
                damageSFX.play(0)
                lives -= 1
                INVT = LT + 120
                break
        for i in LaserEnemies:
            if player.colliderect(i[0]) and i[4]:
                damageSFX.play(0)
                lives -= 1
                INVT = LT + 120
                break
        for i in GlideEnemies:
            if player.colliderect(i[1]):
                damageSFX.play(0)
                lives -= 1
                INVT = LT + 120
                break

        # LAG FIX HERE
        if LT % 30 == 0:
            for i in SpinEnemies:
                rotated = pygame.transform.rotate(i[0], i[5])
                rect = rotated.get_rect(center=(i[1], i[2]))
                mask = pygame.mask.from_surface(rotated)
                offset = (player.x - rect.x, player.y - rect.y)
                if mask.overlap(player_mask, offset) and i[10]:
                    damageSFX.play(0)
                    lives -= 1
                    INVT = LT + 120
                    break
    return lives, INVT

def keyBinds(paused, LT, debug):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return -1
            elif event.key == pygame.K_p:
                if paused:
                    pygame.mixer.music.unpause()
                    return 0
                else:
                    pygame.mixer.music.pause()
                    drawText(font, "Game Paused", "white", 550, 340, 255)
                    pygame.display.flip()
                    return 1
        elif debug and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                print("Frame #: " + str(LT))
                print("M-Pos: ", pygame.mouse.get_pos())
                print("P-Pos: ", player.centerx, player.centery)
    return paused

#Debug function
async def debugFunction(debug):
    if not debug:
        return 0, False
    debugF = 0
    text = 'Starting Frame'
    textbox = pygame.Rect(520, 240, 240, 40)
    debugINVT = False
    rectDebugINVT = pygame.Rect(540, 340, 40, 40)
    active = False
    set = not debug

    while not set:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return -1, False
                if active:
                    if event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
                if event.key == pygame.K_RETURN:
                    active = False
                    try:
                        debugF = max(0, int(text))
                        set = True
                    except Exception:
                        text = "Bad Input"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if textbox.collidepoint(event.pos):
                        text = ""
                        active = True
                    else:
                        active = False
                    if rectDebugINVT.collidepoint(event.pos):
                        debugINVT = not debugINVT

        drawText(pygame.font.Font(None, 64), "Debug Menu", "pink", 500, 140, 255)
        pygame.draw.rect(screen, "white", textbox)
        drawText(font, text, "black", 540, 248, 255)
        drawText(font, "God Mode", "white", 600, 348, 255)
        if debugINVT:
            pygame.draw.rect(screen, "green", rectDebugINVT)
        else:
            pygame.draw.rect(screen, "red", rectDebugINVT)

        pygame.display.flip()
        await asyncio.sleep(0)
    return debugF, debugINVT

#Levels
async def level_1(debug):
    global globalTimer
    pygame.mixer.music.unload()
    bpm = 132
    activeMusic = False
    start = 260
    LT = 0
    INVT = 0
    fpb = 3600/bpm
    lives=3
    paused = False

    #Use aprox values
    beats1 = [i for i in range(0, 50, 10)]
    beats1.extend([round(i) for i in range(round(2 * fpb), 50 + round(2 * fpb), 10)])
    beats1.extend([round(i) for i in range(round(4 * fpb), 50 + round(4 * fpb), 10)])
    beats1.extend([round(i) for i in range(round(6 * fpb), 50 + round(6 * fpb), 10)])
    pos1 = [i for i in range(0, 720, 144)]
    pos1.extend([i for i in range(36, 720, 144)])
    pos1.extend([i for i in range(72, 720, 144)])
    pos1.extend([i for i in range(108, 720, 144)])
    beats2 = [round(i * fpb) for i in range(28)]
    beats3 = [round(i * fpb / 2) for i in range(12 * 2)]  # half-beats
    beats4 = [round(i * fpb) for i in range(12)]  # full beats
    beats5 = [round(i * fpb / 2) for i in range(4 * 2)]  # half-beats, 4 beats long
    beats6 = [round(i * fpb * 2) for i in range(28 // 2)]  # every 2 beats
    beats7 = [round(i * fpb / 4) for i in range(36 * 4)]  # quarter-beats

    #Use precise values
    refBeat = [start, start+round(16*3600/bpm), start+round(32*fpb), start+round(48*3600/bpm),
               start+round(56*fpb), start+round(64*fpb), start+round(96*fpb)]

    player.centerx = width / 2
    player.centery = height / 2

    debugF, debugINVT = await debugFunction(debug)
    if debugF == -1:
        return
    if debugINVT:
        INVT = 99999

    while not lives==0:
        # Handle events
        paused = keyBinds(paused, LT, debug)

        #Core game code
        if paused==-1:
            player.centerx = width / 2
            player.centery = height / 2
            return
        elif paused==0:
            screen.fill("black")
            globalTimer+=1
            #Fading text
            if LT<=240:
                fs, fe = 180, 240
                musicFontAnimation(globalTimer, 30, 40)
                if fs <= LT <= fe:
                    alpha = 255 * (1 - (LT - fs) / (fe - fs))
                    drawText(font, "Coconut Mall", "white", 830, 600, alpha)
                    drawText(musicFont, "♫", "green",  800, 620, alpha)
                    drawText(musicFont, "♫", "green", 1240, 620, alpha)
                    drawText(font, "Ryu Nagamatsu & Asuka Ohta", "white", 830, 650, alpha)
                elif LT < fs:
                    drawText(font, "Coconut Mall", "white", 830, 600, 255)
                    drawText(musicFont, "♫", "green",  800, 620, 255)
                    drawText(musicFont, "♫", "green", 1240, 620, 255)
                    drawText(font, "Ryu Nagamatsu & Asuka Ohta", "white", 830, 650, 255)
            if LT >= start and not activeMusic:
                pygame.mixer.music.load(musicFolder + RectLevelMusic[0][1])
                if debug:
                    LT=max(debugF, start)
                pygame.mixer.music.play(loops=0, start=(LT - start) / 60)
                activeMusic = True

            # Handle enemy logic
            enemyLogic(LT)

            # Enemies start here
            for i, j in zip(beats1, pos1):
                if LT == refBeat[0] + i:
                    RectEnemies.append(generateBasic(1280, j, 36, 36, -7, 0))
            for i in beats2:
                if LT == refBeat[1] + i:
                    RectEnemies.append(generateBasic(1280, random.randint(0, 620), 100, 100, -10, 0))
            for i in beats3:
                if LT == refBeat[2] + i:
                    RectEnemies.append(generateBasic(1280, random.randint(0, 688), 32, 32, -15, 0))
            for i in beats4:
                if LT == refBeat[3] + i:
                    RectEnemies.append(generateBasic(-100, random.randint(0, 620), 100, 100, 10, 0))
            for i in beats5:
                if LT == refBeat[4] + i:
                    RectEnemies.append(generateBasic(-32, random.randint(0, 688), 32, 32, 15, 0))
            for i in beats6:
                if LT == refBeat[5] + i:
                    top = random.randint(120, 600)
                    RectEnemies.append(generateBasic(1280, 0, 50, top, -10, 0))
                    RectEnemies.append(generateBasic(1280, top+80, 50, 720-top-80, -10, 0))
            for i in beats7:
                if LT == refBeat[6] + i:
                    if LT%4==0:
                        RectEnemies.append(generateBasic(1280, random.randint(0, 710), 15, 15, -10, 0))
                    else:
                        RectEnemies.append(generateBasic(-15, random.randint(0, 710), 15, 15, 10, 0))
            # Enemies end here

            #Player movement
            movePlayer(player)

            #I frames
            lives, INVT = invCheck(lives, INVT, LT, None)

            #End of level
            if(LT>=start+round(144*fpb)):
                player.centerx = width / 2
                player.centery = height / 2
                lives=0
                print("You win")

            #Damage taken

            damageCheck(lives, INVT, LT)

            #Ticks and Display
            pygame.display.flip()
            fps.tick(60)
            LT += 1
            await asyncio.sleep(0)

async def level_2(debug):
    global globalTimer
    pygame.mixer.music.unload()
    bpm = 174
    activeMusic = False
    start = 260
    switch = True
    switch2 = True
    LT = 0
    INVT = 0
    fpb = 3600 / bpm
    lives = 3
    paused = False

    # Use aprox values
    beats1 = [round(i*fpb*4) for i in range(60//4)]
    beats2 = [round(i*fpb) for i in range(52)]
    beats3 = [round(i*fpb*4) for i in range(28//4)]
    beats4 = [round(i*fpb) for i in range(12)]
    beats5 = [round(i*fpb) for i in range(12)]
    beats6 = [round(i*fpb) for i in range(12)]
    beats7 = [round(i*fpb/2) for i in range(2*2)]
    beats7.extend([round(i*fpb/2) for i in range(4*2, 6*2)])
    beats7.extend([round(i*fpb/2) for i in range(8*2, 10*2)])
    beats8 = [round(i * fpb / 2) for i in range(2 * 2, 4*2)]
    beats8.extend([round(i * fpb / 2) for i in range(6 * 2, 8*2)])
    beats8.extend([round(i * fpb / 2) for i in range(10 * 2, 12*2)])
    beats9 = [round(i*fpb*4) for i in range(28//4)]
    beats10 = [round(i*fpb*4) for i in range(28//4)]
    beats11 = [round(i*fpb) for i in range(60)]
    beats12 = [round(i*fpb*4) for i in range(60//4)]

    # Use precise values
    refBeat = [start, start + round(64*fpb), start + round(96*fpb), start + round(128*fpb),
               start + round(144*fpb), start + round(160*fpb), start + round(176*fpb), start + round(192*fpb),
               start + round(224*fpb), start + round(272*fpb)]

    player.centerx = width / 2
    player.centery = height / 2

    debugF, debugINVT = await debugFunction(debug)
    if debugF == -1:
        return
    if debugINVT:
        INVT = 99999

    while not lives==0:
        # Handle events
        paused = keyBinds(paused, LT, debug)

        # Core game code
        if paused==-1:
            player.centerx = width / 2
            player.centery = height / 2
            return
        elif paused==0:
            screen.fill("black")
            globalTimer += 1
            # Fading text
            if LT <= 240:
                fs, fe = 180, 240
                musicFontAnimation(globalTimer, 30, 40)
                if fs <= LT <= fe:
                    alpha = 255 * (1 - (LT - fs) / (fe - fs))
                    drawText(font, "Focus", "white", 830, 600, alpha)
                    drawText(musicFont, "♫", "green", 800, 620, alpha)
                    drawText(musicFont, "♫", "green", 940, 620, alpha)
                    drawText(font, "Chipzel", "white", 830, 650, alpha)
                elif LT < fs:
                    drawText(font, "Focus", "white", 830, 600, 255)
                    drawText(musicFont, "♫", "green", 800, 620, 255)
                    drawText(musicFont, "♫", "green", 940, 620, 255)
                    drawText(font, "Chipzel", "white", 830, 650, 255)
            if LT >= start and not activeMusic:
                pygame.mixer.music.load(musicFolder + RectLevelMusic[1][1])
                if debug:
                    LT = max(debugF, start)
                pygame.mixer.music.play(loops=0, start=(LT - start) / 60)
                activeMusic = True

            # Handle enemy logic
            enemyLogic(LT)

            # Enemies start here
            for i in beats1:
                if LT == refBeat[0] + i:
                    ExplodeEnemies.append(generateExploding(1280, random.randint(0, 670), 50, 50, -10, 0, LT + int(2*fpb), 10, 10, 15, 16))
            for i in beats2:
                if LT == refBeat[1] + i:
                    if switch:
                        RectEnemies.append(generateBasic(1280, random.randint(0, 620), 10, 100, -5, 0))
                    else:
                        RectEnemies.append(generateBasic(-10, random.randint(0, 620), 10, 100, 5, 0))
                    switch = not switch
            for i in beats3:
                if LT == refBeat[2] + i:
                    ExplodeEnemies.append(generateExploding(1280, random.randint(0, 695), 50, 50, -10, 0, LT + int(2*fpb), 10, 10, 15, 16))
            for i in beats4:
                if LT == refBeat[3] + i:
                    ExplodeEnemies.append(generateExploding(1280, random.randint(0, 695), 25, 25, -10, 0, LT + int(2 * fpb), 5, 5,10, 12))
            for i in beats5:
                if LT == refBeat[4] + i:
                    ExplodeEnemies.append(generateExploding(-25, random.randint(0, 695), 25, 25, 10, 0, LT + int(2 * fpb), 5, 5,10, 12))
            for i in beats6:
                if LT == refBeat[5] + i:
                    ExplodeEnemies.append(generateExploding(1280, random.randint(0, 695), 25, 25, -10, 0, LT + int(2 * fpb), 5, 5,10, 12))
            for i in beats7:
                if LT == refBeat[6] + i:
                    if switch:
                        ExplodeEnemies.append(generateExploding(1280, random.randint(0, 695), 25, 25, -10, 0, LT + int(2 * fpb), 5, 5,10, 8))
                    else:
                        ExplodeEnemies.append(generateExploding(-25, random.randint(0, 695), 25, 25, 10, 0, LT + int(2 * fpb), 5, 5,10, 8))
                    switch = not switch
            for i in beats8:
                if LT == refBeat[6] + i:
                    if switch2:
                        RectEnemies.append(generateBasic(1280, random.randint(0, 670), 50, 50, -15, 0))
                    else:
                        RectEnemies.append(generateBasic(-50, random.randint(0, 670), 50, 50, 15, 0))
                    switch2 = not switch2
            for i in beats9:
                if LT == refBeat[7] + i:
                    if switch:
                        RectEnemies.append(generateBasic(0, -20, 800, 20, 0, 5))
                    else:
                        RectEnemies.append(generateBasic(480, -20, 800, 20, 0, 5))
                    switch = not switch
            for i in beats10:
                if LT == refBeat[8] + i:
                    if switch:
                        RectEnemies.append(generateBasic(0, 720, 800, 20, 0, -5))
                    else:
                        RectEnemies.append(generateBasic(480, 720, 800, 20, 0, -5))
                    switch = not switch
            for i in beats11:
                if LT == refBeat[9] + i:
                    RectEnemies.append(generateBasic(random.randint(0, 1230), -50, 50, 50, 0, 10))
            for i in beats12:
                if LT == refBeat[9] + i:
                    if switch:
                        ExplodeEnemies.append(
                            generateExploding(1280, random.randint(0, 670), 50, 50, -10, 0, LT + int(2 * fpb), 10, 10, 10,12))
                    else:
                        ExplodeEnemies.append(
                            generateExploding(-25, random.randint(0, 670), 50, 50, 10, 0, LT + int(2 * fpb), 10, 10, 10,12))
                    switch = not switch
            # Enemies end here

            # Player movement
            movePlayer(player)

            # I frames
            lives, INVT = invCheck(lives, INVT, LT, None)

            # End of level
            if LT >= start + round(340 * fpb):
                player.centerx = width / 2
                player.centery = height / 2
                lives=0
                print("You win")

            # Damage taken
            damageCheck(lives, INVT, LT)

            # Ticks and Display
            pygame.display.flip()
            fps.tick(60)
            LT += 1
            await asyncio.sleep(0)

async def level_3(debug):
    pygame.mixer.music.unload()
    bpm = 143
    activeMusic = False
    start = 300
    switch = True
    flashing = False
    time = 0
    diff = 0
    color1 = (0, 0, 0)
    color2 = (0, 0, 0)
    global Gvx, Gvy, globalTimer
    LT = 0
    INVT = 0
    fpb = 3600 / bpm
    lives = 3
    paused = False

    # Use aprox values
    beats1 = [round(i * fpb) for i in range(22)]
    beats2 = [round(i * fpb * 4) for i in range(7)]
    beats3 = [round(i * fpb / 2) for i in range(54)]

    # Use precise values
    refBeat = [start, start + round(26 * fpb), start + round(58 * fpb), start + round(90 * fpb)]
    player_mask = pygame.Mask(player.size, fill=True)

    player.centerx = width / 2
    player.centery = height / 2

    debugF, debugINVT = await debugFunction(debug)
    if debugF == -1:
        return
    if debugINVT:
        INVT = 99999

    while not lives == 0:

        # Handle events
        paused = keyBinds(paused, LT, debug)

        # Core game code
        if paused==-1:
            player.centerx = width / 2
            player.centery = height / 2
            return
        elif paused==0:
            if not flashing:
                screen.fill(color1)
            else:
                transitionColor(LT, time, diff, color1, color2)
                if LT >= time:
                    flashing = False
                    color1 = color2
            globalTimer += 1
            # Fading text
            if LT <= 240:
                fs, fe = 180, 240
                musicFontAnimation(globalTimer, 30, 40)
                if fs <= LT <= fe:
                    alpha = 255 * (1 - (LT - fs) / (fe - fs))
                    drawText(font, "Factory", "white", 830, 600, alpha)
                    drawText(musicFont, "♫", "green", 800, 620, alpha)
                    drawText(musicFont, "♫", "green", 1060, 620, alpha)
                    drawText(font, "Danimal Cannon", "white", 830, 650, alpha)
                elif LT < fs:
                    drawText(font, "Factory", "white", 830, 600, 255)
                    drawText(musicFont, "♫", "green", 800, 620, 255)
                    drawText(musicFont, "♫", "green", 1060, 620, 255)
                    drawText(font, "Danimal Cannon", "white", 830, 650, 255)
            if LT >= start and not activeMusic:
                pygame.mixer.music.load(musicFolder + RectLevelMusic[2][1])
                if debug:
                    LT = max(debugF, start)
                pygame.mixer.music.play(loops=0, start=(LT - start) / 60)
                activeMusic = True

            # Handle enemy logic
            enemyLogic(LT)
            #x, y, w, h, LT, dur, warn, x2, y2, vx, vy, t
            # Enemies start here
            for i in beats1:
                switch = random.randint(0, 1)
                if LT == refBeat[0] + i:
                    if switch:
                        LaserEnemies.append(
                            generateLaser(random.randint(0, 1230), 0, 50, 720, LT + round(2 * fpb), round(fpb),
                                          round(2 * fpb)))
                    else:
                        LaserEnemies.append(
                            generateLaser(0, random.randint(0, 670), 1280, 50, LT + round(2 * fpb), round(fpb),
                                          round(2 * fpb)))
            if LT == refBeat[1] - round(4 * fpb):
                GlideEnemies.append(generateGliding(0, 0, 380, 720, LT + round(2 * fpb), round(64 * fpb),
                                          round(2 * fpb), -380, 0, 10, 0, 38))
                GlideEnemies.append(generateGliding(900, 0, 380, 720, LT + round(2 * fpb), round(64 * fpb),
                                                    round(2 * fpb), 1280, 0, -10, 0, 38))
                GlideEnemies.append(generateGliding(380, 0, 520, 20, LT + round(2 * fpb), round(64 * fpb),
                                                    round(2 * fpb), 380, -20, 0, 1, 20))
                GlideEnemies.append(generateGliding(380, 700, 520, 20, LT + round(2 * fpb), round(64 * fpb),
                                                    round(2 * fpb), 380, 720, 0, -1, 20))
            if LT == refBeat[1]:
                Gvy=3
            for i in beats2:
                if LT == refBeat[1] + i:
                    LaserEnemies.append(
                        generateLaser(0, random.randint(0, 520), 1280, 200, LT + round(2 * fpb), round(2 *fpb),
                                      round(2 * fpb)))
            if LT == refBeat[2]:
                Gvy=0
                Gvx=2
            for i in beats3:
                if LT == refBeat[2] + i:
                    LaserEnemies.append(
                        generateLaser(random.randint(380, 890), 0, 10, 720, LT + round(2 * fpb), round(fpb),
                                      round(2 * fpb)))
            if LT == refBeat[3]:
                Gvx=0
            # Enemies end here

            # Player movement
            movePlayer(player)

            # I frames
            lives, INVT = invCheck(lives, INVT, LT, player_mask)

            # End of level
            if LT >= start + round(100 * fpb):
                player.centerx = width / 2
                player.centery = height / 2
                lives = 0
                print("You win")

            # Damage taken
            damageCheck(lives, INVT, LT)

            # Ticks and Display
            pygame.display.flip()
            fps.tick(60)
            LT += 1
            await asyncio.sleep(0)

async def level_4(debug):
    global globalTimer
    pygame.mixer.music.unload()
    bpm = 133
    activeMusic = False
    start = 300
    switch = True
    flashing = False
    time = 0
    diff = 0
    color1 = (0, 0, 0)
    color2 = (0, 0, 0)
    LT = 0
    INVT = 0
    fpb = 3600 / bpm
    lives = 3
    paused = False

    # Use aprox values
    beats1 = [round(i * fpb) for i in range(60)]
    beats2 = [round(i * fpb) for i in range(28)]
    beats3 = [round(i * fpb) for i in range(28)]
    beats4 = [round(i * fpb*2) for i in range(30)]
    beats5 = [round(i * fpb*2) for i in range(6)]

    # Use precise values
    refBeat = [start, start + round(64*fpb), start + round(96*fpb), start + round(128*fpb),
               start + round(160*fpb), start + round(192*fpb)]
    player_mask = pygame.Mask(player.size, fill=True)

    player.centerx = width / 2
    player.centery = height / 2

    debugF, debugINVT = await debugFunction(debug)
    if debugF == -1:
        return
    if debugINVT:
        INVT = 99999

    while not lives==0:

        # Handle events
        paused = keyBinds(paused, LT, debug)

        # Core game code
        if paused==-1:
            player.centerx = width / 2
            player.centery = height / 2
            return
        elif paused==0:
            if not flashing:
                screen.fill(color1)
            else:
                transitionColor(LT, time, diff, color1, color2)
                if LT>=time:
                    flashing = False
                    color1=color2
            globalTimer += 1
            # Fading text
            if LT <= 240:
                fs, fe = 180, 240
                musicFontAnimation(globalTimer, 30, 40)
                if fs <= LT <= fe:
                    alpha = 255 * (1 - (LT - fs) / (fe - fs))
                    drawText(font, "Sevcon", "white", 830, 600, alpha)
                    drawText(musicFont, "♫", "green", 800, 620, alpha)
                    drawText(musicFont, "♫", "green", 1070, 620, alpha)
                    drawText(font, "Big Giant Circles", "white", 830, 650, alpha)
                elif LT < fs:
                    drawText(font, "Sevcon", "white", 830, 600, 255)
                    drawText(musicFont, "♫", "green", 800, 620, 255)
                    drawText(musicFont, "♫", "green", 1070, 620, 255)
                    drawText(font, "Big Giant Circles", "white", 830, 650, 255)
            if LT >= start and not activeMusic:
                pygame.mixer.music.load(musicFolder + RectLevelMusic[3][1])
                if debug:
                    LT = max(debugF, start)
                pygame.mixer.music.play(loops=0, start=(LT - start) / 60)
                activeMusic = True

            # Handle enemy logic
            enemyLogic(LT)

            # Enemies start here
            if LT == refBeat[0] - round(2 * fpb):
                LaserEnemies.append(generateLaser(600, 320, 80, 80, LT + round(2 * fpb), round(60*fpb),
                                                  round(2 * fpb)))
                LaserEnemies.append(generateLaser(0, 0, 50, 720, LT + round(2 * fpb), round(124 * fpb),
                                                  round(2 * fpb)))
                LaserEnemies.append(generateLaser(1230, 0, 50, 720, LT + round(2 * fpb), round(124 * fpb),
                                                  round(2 * fpb)))
                LaserEnemies.append(generateLaser(0, 0, 1280, 50, LT + round(2 * fpb), round(124 * fpb),
                                                  round(2 * fpb)))
                LaserEnemies.append(generateLaser(0, 680, 1280, 50, LT + round(2 * fpb), round(124 * fpb),
                                                  round(2 * fpb)))
            for i in beats1:
                a = random.randint(0, 12)
                b = random.randint(0, 8)
                if a<6 and b<4:
                    a += 6
                    b += 4
                if LT == refBeat[0] + i:
                    RectEnemies.append(generateBasic(635, 355, 15, 15, a, b))
                    RectEnemies.append(generateBasic(635, 355, 15, 15, a, -b))
                    RectEnemies.append(generateBasic(635, 355, 15, 15, -a, -b))
                    RectEnemies.append(generateBasic(635, 355, 15, 15, -a, b))
            if LT == refBeat[0]+round(32*fpb):
                flashing = True
                color1=(0, 0, 0)
                color2=(100, 0, 100)
                time = LT + round(32 * fpb)
                diff = time-LT
            for i in beats2:
                if LT == refBeat[1] + i:
                    LaserEnemies.append(generateLaser(random.randint(50, 1180), 0, 50, 720, LT + round(2*fpb), round(fpb), round(2*fpb)))
                    LaserEnemies.append(generateLaser(0, random.randint(50, 620), 1280, 50, LT + round(2*fpb), round(fpb), round(2*fpb)))
            for i in beats3:
                if LT == refBeat[2] + i:
                    LaserEnemies.append(
                        generateLaser(random.randint(80, 1150), 0, 80, 720, LT + round(2 * fpb), round(fpb),
                                      round(2 * fpb)))
                    LaserEnemies.append(
                        generateLaser(0, random.randint(80, 590), 1280, 80, LT + round(2 * fpb), round(fpb),
                                      round(2 * fpb)))
            if LT == refBeat[3] - round(4 * fpb):
                LaserEnemies.append(generateLaser(0, 0, 80, 720, LT + round(4 * fpb), round(60 * fpb),
                                                  round(4 * fpb)))
                LaserEnemies.append(generateLaser(1200, 0, 80, 720, LT + round(4 * fpb), round(60 * fpb),
                                                  round(4 * fpb)))
                LaserEnemies.append(generateLaser(0, 0, 1280, 80, LT + round(4 * fpb), round(60 * fpb),
                                                  round(4 * fpb)))
                LaserEnemies.append(generateLaser(0, 640, 1280, 80, LT + round(4 * fpb), round(60 * fpb),
                                                  round(4 * fpb)))
            if LT == refBeat[3] - round(4 * fpb):
                SpinEnemies.append(
                    generateSpinning(640, 360, 20, 1280, 0, 0, 0, 0.5, LT + round(4 * fpb), round(60 * fpb), round(4 * fpb)))
                flashing = True
                color1 = (100, 0, 100)
                color2 = (0, 64, 0)
                time = LT + round(4 * fpb)
                diff = time - LT
            for i in beats4:
                if LT == refBeat[3] + i:
                    if switch:
                        LaserEnemies.append(
                            generateLaser(random.randint(80, 1100), 0, 100, 720, LT + round(2 * fpb), round(fpb),
                                          round(2 * fpb)))
                    else:
                        LaserEnemies.append(
                            generateLaser(0, random.randint(80, 540), 1280, 100, LT + round(2 * fpb), round(fpb),
                                          round(2 * fpb)))
                    switch = not switch
            if LT == refBeat[4] - round(4 * fpb):
                SpinEnemies.append(
                    generateSpinning(640, 360, 20, 1280, 0, 0, 55, 0.7, LT + round(4 * fpb), round(28 * fpb), round(4 * fpb)))
            if LT == refBeat[5]:
                flashing = True
                color1 = (0, 64, 0)
                color2 = (48, 196, 209)
                time = LT + round(4 * fpb)
                diff = time - LT
                for i in range(10):
                    LaserEnemies.append(
                        generateLaser(i * 1280 // 10, 648 - i * 72, 1280 // 10, 72 + 72 * i, LT + round(3 * fpb),
                                      round(12 * fpb),
                                      round(3 * fpb)))
            for i in beats5:
                if LT == refBeat[5] + i+round(3 * fpb):
                    if switch:
                        ExplodeEnemies.append(generateExploding(-50, random.randint(0, 335), 50, 50, 10, 0, LT + round(fpb), 10, 10, 10, 8))
                    else:
                        ExplodeEnemies.append(generateExploding(random.randint(0, 615), -50, 50, 50, 0, 10, LT + round(fpb), 10, 10, 10, 8))
                    switch = not switch
            if LT == refBeat[5]+round(16 * fpb):
                flashing = True
                color1 = (48, 196, 209)
                color2 = (72, 171, 70)
                time = LT + round(4 * fpb)
                diff = time - LT
                for i in range(10):
                    LaserEnemies.append(
                        generateLaser(i*1280//10, i*72, 1280//10, 720-72*i, LT + round(3 * fpb), round(12 * fpb),
                                      round(3 * fpb)))
            for i in beats5:
                if LT == refBeat[5] + i+round(19 * fpb):
                    if switch:
                        ExplodeEnemies.append(generateExploding(1280, random.randint(0, 335), 50, 50, -10, 0, LT + round(fpb), 10, 10, 10, 8))
                    else:
                        ExplodeEnemies.append(generateExploding(random.randint(615, 1230), -50, 50, 50, 0, 10, LT + round(fpb), 10, 10, 10, 8))
                    switch = not switch
            if LT == refBeat[5]+round(32 * fpb):
                flashing = True
                color1 = (72, 171, 70)
                color2 = (212, 194, 76)
                time = LT + round(4 * fpb)
                diff = time - LT
                for i in range(10):
                    LaserEnemies.append(
                        generateLaser(i * 1280 // 10, 0, 1280 // 10, 72 + 72 * i, LT + round(3 * fpb),
                                      round(12 * fpb),
                                      round(3 * fpb)))
            for i in beats5:
                if LT == refBeat[5] + i+round(35 * fpb):
                    if switch:
                        ExplodeEnemies.append(generateExploding(-50, random.randint(335, 670), 50, 50, 10, 0, LT + round(fpb), 10, 10, 10, 8))
                    else:
                        ExplodeEnemies.append(generateExploding(random.randint(0, 615), 720, 50, 50, 0, -10, LT + round(fpb), 10, 10, 10, 8))
                    switch = not switch
            if LT == refBeat[5] + round(48 * fpb):
                flashing = True
                color1 = (212, 194, 76)
                color2 = (173, 42, 79)
                time = LT + round(4 * fpb)
                diff = time - LT
                for i in range(10):
                    LaserEnemies.append(
                        generateLaser(i * 1280 // 10, 0, 1280 // 10, 720 - 72 * i, LT + round(3 * fpb), round(12 * fpb),
                                      round(3 * fpb)))
            for i in beats5:
                if LT == refBeat[5] + i+round(51 * fpb):
                    if switch:
                        ExplodeEnemies.append(generateExploding(1280, random.randint(335, 670), 50, 50, -10, 0, LT + round(fpb), 10, 10, 10, 8))
                    else:
                        ExplodeEnemies.append(generateExploding(random.randint(615, 1230), 720, 50, 50, 0, -10, LT + round(fpb), 10, 10, 10, 8))
                    switch = not switch
            # Enemies end here

            # Player movement
            movePlayer(player)

            # I frames
            lives, INVT = invCheck(lives, INVT, LT, player_mask)

            # End of level
            if LT >= start + round(256 * fpb):
                player.centerx = width / 2
                player.centery = height / 2
                lives=0
                print("You win")

            # Damage taken
            damageCheck(lives, INVT, LT)

            # Ticks and Display
            pygame.display.flip()
            fps.tick(60)
            LT += 1
            await asyncio.sleep(0)

async def level_5(debug):
    global globalTimer
    pygame.mixer.music.unload()
    bpm = 183
    activeMusic = False
    start = 260
    switch = True
    flashing = False
    time = 0
    diff = 0
    color1 = (0, 0, 0)
    color2 = (0, 0, 0)
    LT = 0
    INVT = 0
    fpb = 3600 / bpm
    lives = 3
    paused = False

    # Use aprox values
    beats1 = [round(i * fpb/2) for i in range(44*2)]
    beats2 = [round(i * fpb) for i in range(0, 28)]
    beats3 = [round(i * fpb) for i in range(0, 28)]
    beats4 = [round(i * fpb) for i in range(0, 28)]
    beats5 = [round(i * fpb) for i in range(0, 28)]
    beats6 = [round(i * fpb) for i in range(0, 28)]
    beats7 = [round(i * fpb) for i in range(0, 32)]
    beats8 = [round(i * fpb/2) for i in range(0, 52)]
    beats9 = [round(i * fpb*2) for i in range(0, 14)]
    beats10 = [round(i * fpb*2) for i in range(0, 14)]

    # Use precise values
    refBeat = [start, start + round(16*fpb), start + round(48*fpb), start + round(80*fpb), start + round(112*fpb),
               start + round(144*fpb), start + round(176*fpb), start + round(212*fpb), start + round(244*fpb),
               start + round(276*fpb), start + round(308*fpb)]

    player.centerx = width / 2
    player.centery = height / 2

    debugF, debugINVT = await debugFunction(debug)
    if debugF == -1:
        return
    if debugINVT:
        INVT = 99999

    while not lives==0:
        # Handle events
        paused = keyBinds(paused, LT, debug)

        # Core game code
        if paused==-1:
            player.centerx = width / 2
            player.centery = height / 2
            return
        elif paused==0:
            if not flashing:
                screen.fill(color1)
            else:
                transitionColor(LT, time, diff, color1, color2)
                if LT>=time:
                    flashing = False
                    color1=color2
            globalTimer += 1
            # Fading text
            if LT <= 240:
                fs, fe = 180, 240
                musicFontAnimation(globalTimer, 30, 40)
                if fs <= LT <= fe:
                    alpha = 255 * (1 - (LT - fs) / (fe - fs))
                    drawText(font, "Milky Ways", "white", 830, 600, alpha)
                    drawText(musicFont, "♫", "green", 800, 620, alpha)
                    drawText(musicFont, "♫", "green", 960, 620, alpha)

                    drawText(font, "Bossfight", "white", 830, 650, alpha)
                elif LT < fs:
                    drawText(font, "Milky Ways", "white", 830, 600, 255)
                    drawText(musicFont, "♫", "green", 800, 620, 255)
                    drawText(musicFont, "♫", "green", 960, 620, 255)
                    drawText(font, "Bossfight", "white", 830, 650, 255)
            if LT >= start and not activeMusic:
                pygame.mixer.music.load(musicFolder + RectLevelMusic[4][1])
                if debug:
                    LT = max(debugF, start)
                pygame.mixer.music.play(loops=0, start=(LT - start) / 60)
                activeMusic=True

            # Handle enemy logic
            enemyLogic(LT)

            # Enemies start here
            for i in beats1:
                if LT == refBeat[0] + i:
                    RectEnemies.append(generateBasic(random.randint(0, 1260), -20, 20, 20, 0, 15))
            if LT == refBeat[1]:
                flashing = True
                color1=(0, 0, 0)
                color2=(40, 10, 40)
                time = LT + round(32 * fpb)
                diff = time-LT
            for i in beats2:
                if LT == refBeat[1] + i:
                    if switch:
                        a = random.randint(0, 590)
                    else:
                        a = random.randint(591, 1180)
                    RectEnemies.append(generateBasic(a, -100, 100, 100, 0, 10))
                    for j in range(1, 4):
                        RectEnemies.append(generateBasic(a+25, -100-60*j, 50, 50, 0, 10))
                    switch = not switch
            if LT == refBeat[2] - round(4*fpb):
                for i in range(1, 6):
                    ExplodeEnemies.append(
                        generateExploding(1280, 120*i, 50, 50, -2, 0, LT + round(4 * fpb), 5, 5, 8,24))
                GlideEnemies.append(generateGliding(10, 0, 50, 720, LT + round(4 * fpb / 2), round(28 * fpb),
                                                    round(4 * fpb / 2), 10, -720, 0, 72, 10))
                GlideEnemies.append(generateGliding(70, 0, 50, 720, LT + round(5 * fpb / 2), round(28 * fpb),
                                                    round(5 * fpb / 2), 70, 720, 0, -72, 10))
                GlideEnemies.append(generateGliding(130, 0, 50, 720, LT + round(6 * fpb / 2), round(28 * fpb),
                                                    round(6 * fpb / 2), 130, -720, 0, 72, 10))
                GlideEnemies.append(generateGliding(190, 0, 50, 720, LT + round(7 * fpb / 2), round(28 * fpb),
                                                    round(7 * fpb / 2), 190, 720, 0, -72, 10))
            if LT == refBeat[2]:
                flashing = True
                color1=(255, 255, 255)
                color2=(40, 10, 40)
                time = LT + round(4 * fpb)
                diff = time-LT
            for i in beats3:
                if LT == refBeat[2] + i:
                    ExplodeEnemies.append(generateExploding(1280, random.randint(0, 670), 50, 50, -10, 0, LT + round(fpb), 10, 10, 15, 16))
            if LT == refBeat[3] - round(4*fpb):
                for i in range(1, 6):
                    ExplodeEnemies.append(
                        generateExploding(-50, 120*i, 50, 50, 2, 0, LT + round(4 * fpb), 5, 5, 8,24))
                GlideEnemies.append(generateGliding(1220, 0, 50, 720, LT + round(4 * fpb / 2), round(28 * fpb),
                                                    round(4 * fpb / 2), 1220, -720, 0, 72, 10))
                GlideEnemies.append(generateGliding(1160, 0, 50, 720, LT + round(5 * fpb / 2), round(28 * fpb),
                                                    round(5 * fpb / 2), 1160, 720, 0, -72, 10))
                GlideEnemies.append(generateGliding(1100, 0, 50, 720, LT + round(6 * fpb / 2), round(28 * fpb),
                                                    round(6 * fpb / 2), 1100, -720, 0, 72, 10))
                GlideEnemies.append(generateGliding(1040, 0, 50, 720, LT + round(7 * fpb / 2), round(28 * fpb),
                                                    round(7 * fpb / 2), 1040, 720, 0, -72, 10))
            if LT == refBeat[3]:
                flashing = True
                color1 = (255, 255, 255)
                color2 = (80, 20, 80)
                time = LT + round(4 * fpb)
                diff = time-LT
            for i in beats4:
                if LT == refBeat[3] + i:
                    ExplodeEnemies.append(generateExploding(-50, random.randint(0, 670), 50, 50, 10, 0, LT + round(fpb), 10, 10, 15, 16))
            if LT == refBeat[4]:
                flashing = True
                color1 = (80, 20, 80)
                color2 = (16, 45, 125)
                time = LT + round(4 * fpb)
                diff = time-LT
            for i in beats5:
                if LT == refBeat[4] + i:
                    a = random.randint(0, 680)
                    if switch:
                        RectEnemies.append(generateBasic(1280, a, 40, 40, -15, 0))
                        for j in range(1, 6):
                            RectEnemies.append(generateBasic(1300+30*j, a+10, 20, 20, -15, 0))
                    else:
                        RectEnemies.append(generateBasic(-40, a, 40, 40, 15, 0))
                        for j in range(1, 6):
                            RectEnemies.append(generateBasic(-40 - 30 * j, a+10, 20, 20, 15, 0))
                    switch = not switch
            if LT == refBeat[5] - round(4 * fpb):
                ExplodeEnemies.append(generateExploding(1280, 110, 100, 100, -3, 0, LT + round(4 * fpb), 10, 10, 7, 16))
                ExplodeEnemies.append(generateExploding(1280, 430, 100, 100, -3, 0, LT + round(4 * fpb), 10, 10, 7, 16))
                ExplodeEnemies.append(generateExploding(-100, 110, 100, 100, 2, 0, LT + round(4 * fpb), 10, 10, 7, 16))
                ExplodeEnemies.append(generateExploding(-100, 430, 100, 100, 2, 0, LT + round(4 * fpb), 10, 10, 7, 16))
            if LT == refBeat[5]:
                flashing = True
                color1 = (255, 255, 255)
                color2 = (0, 80, 80)
                time = LT + round(4 * fpb)
                diff = time-LT
            for i in beats6:
                if LT == refBeat[5] + i:
                    a = random.randint(0, 1240)
                    if switch:
                        RectEnemies.append(generateBasic(a, -40, 40, 40, 0, 10))
                        for j in range(1, 6):
                            RectEnemies.append(generateBasic(a+10, -40-30*j, 20, 20, 0, 10))
                    else:
                        RectEnemies.append(generateBasic(a, 720, 40, 40, 0, -10))
                        for j in range(1, 6):
                            RectEnemies.append(generateBasic(a+10, 740+30*j, 20, 20, 0, -10))
                    switch = not switch
            if LT == refBeat[6] - round(2 * fpb):
                flashing = True
                color1 = (0, 80, 80)
                color2 = (150, 30, 68)
                time = LT + round(4 * fpb)
                diff = time-LT
            for i in beats7:
                switch = random.randint(0, 1)
                if LT == refBeat[6] + i:
                    if switch:
                        LaserEnemies.append(generateLaser(random.randint(0, 1180), 0, 100, 720, LT + round(2*fpb), round(fpb), round(2*fpb)))
                    else:
                        LaserEnemies.append(generateLaser(0, random.randint(0, 620), 1280, 100, LT + round(2*fpb), round(fpb), round(2*fpb)))
            if LT == refBeat[7] - round(2 * fpb):
                flashing = True
                color1 = (150, 30, 68)
                color2 = (200, 10, 18)
                time = LT + round(4 * fpb)
                diff = time - LT
            for i in beats8:
                switch = random.randint(0, 1)
                if LT == refBeat[7] + i:
                    if switch:
                        LaserEnemies.append(
                            generateLaser(random.randint(0, 1230), 0, 50, 720, LT + round(2 * fpb), round(fpb),
                                          round(2 * fpb)))
                    else:
                        LaserEnemies.append(
                            generateLaser(0, random.randint(0, 670), 1280, 50, LT + round(2 * fpb), round(fpb),
                                          round(2 * fpb)))
            if LT == refBeat[8] - round(4*fpb):
                flashing = True
                color1 = (200, 10, 18)
                color2 = (128, 0, 128)
                time = LT + round(4 * fpb)
                diff = time - LT
                for i in range(1, 6):
                    ExplodeEnemies.append(generateExploding(1280, 120*i, 50, 50, -2, 0, LT + round(4 * fpb), 5, 5, 8,24))
            if LT == refBeat[8]:
                flashing = True
                color1 = (255, 255, 255)
                color2 = (128, 0, 128)
                time = LT + round(4 * fpb)
                diff = time-LT
            for i in beats9:
                a = random.randint(0, 680)
                switch = random.randint(0, 1)
                if LT == refBeat[8] + i:
                    RectEnemies.append(generateBasic(1280, a, 40, 40, -15, 0))
                    for j in range(1, 6):
                        RectEnemies.append(generateBasic(1300 + 30 * j, a + 10, 20, 20, -15, 0))
                    ExplodeEnemies.append(generateExploding(1280, random.randint(0, 670), 50, 50, -10, 0, LT + round(fpb), 10, 10, 15,16))
                    if switch:
                        LaserEnemies.append(
                            generateLaser(random.randint(0, 1180), 0, 100, 720, LT + round(2 * fpb), round(fpb),
                                          round(2 * fpb)))
                    else:
                        LaserEnemies.append(
                            generateLaser(0, random.randint(0, 620), 1280, 100, LT + round(2 * fpb), round(fpb),
                                          round(2 * fpb)))
            if LT == refBeat[9] - round(4*fpb):
                for i in range(1, 6):
                    ExplodeEnemies.append(generateExploding(-50, 120*i, 50, 50, 2, 0, LT + round(4 * fpb), 5, 5, 8,24))
            if LT == refBeat[9]:
                flashing = True
                color1 = (255, 255, 255)
                color2 = (128, 0, 128)
                time = LT + round(4 * fpb)
                diff = time-LT
            for i in beats10:
                a = random.randint(0, 680)
                switch = random.randint(0, 1)
                if LT == refBeat[9] + i:
                    RectEnemies.append(generateBasic(-40, a, 40, 40, 15, 0))
                    for j in range(1, 6):
                        RectEnemies.append(generateBasic(-40 - 30 * j, a + 10, 20, 20, 15, 0))
                    ExplodeEnemies.append(generateExploding(-50, random.randint(0, 670), 50, 50, 10, 0, LT + round(fpb), 10, 10, 15,16))
                    if switch:
                        LaserEnemies.append(
                            generateLaser(random.randint(0, 1180), 0, 100, 720, LT + round(2 * fpb), round(fpb),
                                          round(2 * fpb)))
                    else:
                        LaserEnemies.append(
                            generateLaser(0, random.randint(0, 620), 1280, 100, LT + round(2 * fpb), round(fpb),
                                          round(2 * fpb)))
            if LT == refBeat[10]:
                flashing = True
                color1 = (128, 0, 128)
                color2 = (0, 0, 0)
                time = LT + round(4 * fpb)
                diff = time-LT
            # Enemies end here

            # Player movement
            movePlayer(player)

            # I frames
            lives, INVT = invCheck(lives, INVT, LT, None)

            # End of level
            if LT >= start + round(316 * fpb):
                player.centerx = width / 2
                player.centery = height / 2
                lives=0
                print("You win")

            # Damage taken
            damageCheck(lives, INVT, LT)

            # Ticks and Display
            pygame.display.flip()
            fps.tick(60)
            LT += 1
            await asyncio.sleep(0)

async def level_6(debug):
    if not debug: return
    pygame.mixer.music.unload()
    bpm = 143
    activeMusic = False
    start = 300
    switch = True
    flashing = False
    time = 0
    diff = 0
    color1 = (0, 0, 0)
    color2 = (0, 0, 0)
    global Gvx, Gvy, globalTimer
    LT = 0
    INVT = 0
    fpb = 3600 / bpm
    lives = 3
    paused = False

    # Use aprox values
    beats1 = [round(i * fpb) for i in range(22)]
    beats2 = [round(i * fpb * 4) for i in range(7)]
    beats3 = [round(i * fpb / 2) for i in range(54)]

    # Use precise values
    refBeat = [start, start + round(26 * fpb), start + round(58 * fpb), start + round(90 * fpb)]
    player_mask = pygame.Mask(player.size, fill=True)

    player.centerx = width / 2
    player.centery = height / 2

    debugF, debugINVT = await debugFunction(debug)
    if debugF == -1:
        return
    if debugINVT:
        INVT = 99999

    while not lives == 0:

        # Handle events
        paused = keyBinds(paused, LT, debug)

        # Core game code
        if paused == -1:
            player.centerx = width / 2
            player.centery = height / 2
            return
        elif paused == 0:
            if not flashing:
                screen.fill(color1)
            else:
                transitionColor(LT, time, diff, color1, color2)
                if LT >= time:
                    flashing = False
                    color1 = color2
            globalTimer += 1
            # Fading text
            if LT <= 240:
                fs, fe = 180, 240
                musicFontAnimation(globalTimer, 30, 40)
                if fs <= LT <= fe:
                    alpha = 255 * (1 - (LT - fs) / (fe - fs))
                    drawText(font, "Tetris", "white", 830, 600, alpha)
                    drawText(musicFont, "♫", "green", 800, 620, alpha)
                    drawText(musicFont, "♫", "green", 1020, 620, alpha)
                    drawText(font, "Purple Fluxxy", "white", 830, 650, alpha)
                elif LT < fs:
                    drawText(font, "Tetris", "white", 830, 600, 255)
                    drawText(musicFont, "♫", "green", 800, 620, 255)
                    drawText(musicFont, "♫", "green", 1020, 620, 255)
                    drawText(font, "Purple Fluxxy", "white", 830, 650, 255)
            if LT >= start and not activeMusic:
                pygame.mixer.music.load(musicFolder + RectLevelMusic[2][1])
                if debug:
                    LT = max(debugF, start)
                pygame.mixer.music.play(loops=0, start=(LT - start) / 60)
                activeMusic = True

            # Handle enemy logic
            enemyLogic(LT)
            # x, y, w, h, LT, dur, warn, x2, y2, vx, vy, t
            # Enemies start here
            for i in beats1:
                switch = random.randint(0, 1)
                if LT == refBeat[0] + i:
                    if switch:
                        LaserEnemies.append(
                            generateLaser(random.randint(0, 1230), 0, 50, 720, LT + round(2 * fpb), round(fpb),
                                          round(2 * fpb)))
                    else:
                        LaserEnemies.append(
                            generateLaser(0, random.randint(0, 670), 1280, 50, LT + round(2 * fpb), round(fpb),
                                          round(2 * fpb)))
            if LT == refBeat[1] - round(4 * fpb):
                GlideEnemies.append(generateGliding(0, 0, 380, 720, LT + round(2 * fpb), round(64 * fpb),
                                                    round(2 * fpb), -380, 0, 10, 0, 38))
                GlideEnemies.append(generateGliding(900, 0, 380, 720, LT + round(2 * fpb), round(64 * fpb),
                                                    round(2 * fpb), 1280, 0, -10, 0, 38))
                GlideEnemies.append(generateGliding(380, 0, 520, 20, LT + round(2 * fpb), round(64 * fpb),
                                                    round(2 * fpb), 380, -20, 0, 1, 20))
                GlideEnemies.append(generateGliding(380, 700, 520, 20, LT + round(2 * fpb), round(64 * fpb),
                                                    round(2 * fpb), 380, 720, 0, -1, 20))
            if LT == refBeat[1]:
                Gvy = 3
            for i in beats2:
                if LT == refBeat[1] + i:
                    LaserEnemies.append(
                        generateLaser(0, random.randint(0, 520), 1280, 200, LT + round(2 * fpb), round(2 * fpb),
                                      round(2 * fpb)))
            if LT == refBeat[2]:
                Gvy = 0
                Gvx = 2
            for i in beats3:
                if LT == refBeat[2] + i:
                    LaserEnemies.append(
                        generateLaser(random.randint(380, 890), 0, 10, 720, LT + round(2 * fpb), round(fpb),
                                      round(2 * fpb)))
            if LT == refBeat[3]:
                Gvx = 0
            # Enemies end here

            # Player movement
            movePlayer(player)

            # I frames
            lives, INVT = invCheck(lives, INVT, LT, player_mask)

            # End of level
            if LT >= start + round(100 * fpb):
                player.centerx = width / 2
                player.centery = height / 2
                lives = 0
                print("You win")

            # Damage taken
            damageCheck(lives, INVT, LT)

            # Ticks and Display
            pygame.display.flip()
            fps.tick(60)
            LT += 1
            await asyncio.sleep(0)

#Main lobby
async def main():
    global activeMusic, volume, busyFading, fading, Gvx, Gvy, screenID, idx, debug, globalTimer
    ticking=False
    alpha=255
    pygame.mixer.music.load(musicFolder + 'Circus.ogg')
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(0)
    while True:
        globalTimer += 1
        Gvx=Gvy=0
        screen.fill("black")
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            elif event.type == pygame.KEYDOWN:
                if screenID == 1:
                    if event.key == code[idx]:
                        idx += 1
                        if idx == 5:
                            debug = not debug
                            idx = 0
                    else:
                        idx=0
                        if event.key == code[idx]:
                            idx += 1
                if event.key == pygame.K_ESCAPE:
                    if screenID != 1:
                        pygame.mixer.music.unload()
                        pygame.mixer.music.load(musicFolder + 'Circus.ogg')
                        pygame.mixer.music.set_volume(0.4)
                        pygame.mixer.music.play(0)
                        alpha=255
                        fading=False
                        screenID=1
                if event.key == pygame.K_RETURN:
                    if screenID==1:
                        ticking=True
                    elif screenID==2 and not activeMusic is None and not busyFading:
                        RectEnemies.clear()
                        ExplodeEnemies.clear()
                        LaserEnemies.clear()
                        GlideEnemies.clear()
                        SpinEnemies.clear()
                        if activeMusic==0:
                            await level_1(debug)
                            fading = True
                        elif activeMusic == 1:
                            await level_2(debug)
                            fading = True
                        elif activeMusic == 2:
                            await level_3(debug)
                            fading = True
                        elif activeMusic == 3:
                            await level_4(debug)
                            fading = True
                        elif activeMusic == 4:
                            await level_5(debug)
                            fading = True
                        elif activeMusic == 5:
                            await level_6(debug)
                            fading = True
        if screenID==1:
            if ticking:
                alpha-=2
                if alpha<=0:
                    ticking=False
                    player.centerx = width / 2
                    player.centery = height / 2
                    pygame.mixer.music.load(musicFolder + RectLobbyMusic)
                    pygame.mixer.music.set_volume(1)
                    fading=False
                    screenID=2

            s = pygame.Surface((350, 180))
            s.set_alpha(alpha)  # alpha level
            s.fill("purple")  # this fills the entire surface
            screen.blit(s, (1280/2-175, 720/2-75))
            musicFontAnimation(globalTimer, 30, 40)
            drawText(musicFont, "♫", "green", 475, 265, alpha)
            drawText(musicFont, "♫", "green", 785, 265, alpha)
            drawText(font, "Project Beats Remix", "skyblue", 505, 300, alpha)
            drawText(font, "By: Jayson Liu", "skyblue", 545, 360, alpha)
            drawText(font, "Press Enter to Continue", "skyblue", 480, 420, alpha)
            if debug:
                drawText(font, "Debug Mode On", "orange", 535, 500, alpha)
        elif screenID==2:
            pygame.draw.rect(screen, "yellow", RectLevelMusic[0][0])
            pygame.draw.rect(screen, "purple", RectLevelMusic[1][0])
            pygame.draw.rect(screen, "red", RectLevelMusic[2][0])
            pygame.draw.rect(screen, "pink", RectLevelMusic[3][0])
            pygame.draw.rect(screen, "navy", RectLevelMusic[4][0])
            pygame.draw.rect(screen, "brown", RectLevelMusic[5][0])
            drawText(font, "Welcome to Project Beats Remix", "white", 430, 300, 255)
            drawText(font, "Go to a level and hit 'Enter' to play", "white", 420, 400, 255)
            drawText(font, "Level 1: Coconut Mall", "purple", 15, 100, 255)
            drawText(font, "Level 2: Focus", "yellow", 380, 100, 255)
            drawText(font, "Level 3: Factory", "cyan", 690, 100, 255)
            drawText(font, "Level 4: Sevcon", "dark green", 1020, 100, 255)
            drawText(font, "Level 5: Milky Ways", "orange", 20, 340, 255)
            drawText(font, "Level 6: ???", "white", 1020, 340, 255)
            drawText(font, "Level 7: ???", "white", 20, 580, 255)
            drawText(font, "Level 8: ???", "white", 380, 580, 255)
            drawText(font, "Level 9: ???", "white", 670, 580, 255)
            drawText(font, "Level 10: ???", "white", 1020, 580, 255)


            musicIndex = None
            for i in range(len(RectLevelMusic)):
                if RectLevelMusic[i][0].collidepoint(player.center):
                    musicIndex = i
                    break
            if musicIndex != activeMusic or busyFading:
                if musicIndex is None and musicIndex != activeMusic and not fading:
                    pygame.mixer.music.load(musicFolder + RectLobbyMusic)
                    pygame.mixer.music.play(0)
                elif musicIndex != activeMusic and not fading:
                    pygame.mixer.music.load(musicFolder + RectLevelMusic[musicIndex][1])
                    pygame.mixer.music.play(0)
                if fading:
                    busyFading = True
                    volume = max(0.0, volume - fade_speed)
                    pygame.mixer.music.set_volume(volume)
                    if volume <= 0.0:
                        fading = False
                else:
                    activeMusic = musicIndex
                    volume = min(1.0, volume + fade_speed)
                    pygame.mixer.music.set_volume(volume)
                    if volume >= 1.0:
                        fading = True
                        busyFading = False
            if not pygame.mixer.music.get_busy():
                try:
                    pygame.mixer.music.play(0)
                except pygame.error:
                    if debug:
                        print("Music Error: No music found. Defaulting to lobby music.")
                    fading=False
                    pygame.mixer.music.load(musicFolder + RectLobbyMusic)
                    pygame.mixer.music.play(0)
            movePlayer(player)
            pygame.draw.rect(screen, "blue", player)



        pygame.display.flip()
        fps.tick(60)
        await asyncio.sleep(0)
asyncio.run(main())