from turtle import *
from time import sleep
import threading
from random import randint


IMAGE_PATHS = ['images/mystery.gif', 'images/ship_1.gif', 'images/ship_2.gif', 'images/ship_3.gif',
               'images/red_mystery.gif']
RIGHT = 1
LEFT = -1
NONE = 0
RIGHT_BOUNDS = 285
LEFT_BOUNDS = -284
SHIPS_IN_ROW = 6
shift = 4
missile_chance = 50
aliens = []
missiles = []
alien_speed = 0.15
earthling_speed = 0.5
game_over = False
level_over = False
destroyed_ships = 0
score = 0
explosion = Turtle()
missile_thread = ""


class ShipIcon(Turtle):
    def __init__(self, img_path):
        super().__init__()
        self.winn = self.screen
        self.winn.addshape(img_path)
        self.shape(img_path)
        self.penup()


class Shooter(Turtle):
    def __init__(self, image_path):
        super().__init__()
        self.setheading(90)
        # self.shape("turtle")
        # self.color('Green')
        # self.image = bgpic(image_path)
        self.t_screen = Screen()
        self.t_screen.addshape(image_path)
        self.shape(image_path)
        self.penup()
        self.hideturtle()
        self.missile_speed = 4
        self.goto(0, -320)
        self.showturtle()

    def move_right(self):
        if self.xcor() < 265:
            self.goto(self.xcor() + 10, self.ycor())

    def move_left(self):
        if self.xcor() > -265:
            self.goto(self.xcor() - 10, self.ycor())

    def fire_missile(self):
        if self.isvisible():
            my_missile = Missile('earthling', (self.xcor(), self.ycor()))
            my_missile.fire()
            missiles.append(my_missile)

    def level_up(self):
        print("new level!")

    def new_ship(self):
        global game_over
        current_ships = int(gui.cv.itemcget(gui.num_ships, 'text')) - 1
        gui.cv.itemconfig(gui.num_ships, text=current_ships)
        if current_ships <= 0:
            game_over = True
            # gui.cv.itemconfig(gui.game_over, text="GAME OVER")
            gui.game_is_over()
        else:
            self.goto(0, -320)
            sleep(0.5)
            if current_ships == 2:
                gui.ship_2.hideturtle()
                gui.ship_2.goto(-400, -400)
            elif current_ships == 1:
                gui.ship_3.hideturtle()
                gui.ship_3.goto(-400, -400)
            self.showturtle()

    def explode(self):
        print("shooter goes BOOM!")
        self.hideturtle()
        explosion.goto(self.xcor(), self.ycor())
        explosion.showturtle()
        sleep(0.15)
        explosion.hideturtle()
        self.new_ship()


class GUI:
    def __init__(self):
        self.high_score = ""
        self.ship_count = 3
        self.score = '0000'

        try:
            with open('high_score.txt', 'r') as f:
                self.high_score = f.read()
                if self.high_score == '':
                    self.high_score = '0000'
        except FileNotFoundError:
            self.high_score = '0000'
        self.cv = screen.getcanvas()
        self.highscore_display = self.cv.create_text(-285, -370, font=("Arial", 18, "normal"), fill="#dddddd",
                                                     text=f"HI-SCORE")
        print(f"self.high_score is {self.high_score}")
        self.highScore = self.cv.create_text(-285, -345, font=("Arial", 18, "bold"), fill="#dddddd",
                                             text=f"{self.high_score}")
        self.score_display = self.cv.create_text(0, -370, font=("Arial", 18, "normal"), fill="#cccccc",
                                                 text=f"SCORE")
        self.score = self.cv.create_text(0, -345, font=("Arial", 18, "bold"), fill="#dddddd", text=f"{self.score}")
        self.num_ships = self.cv.create_text(-275, 365, font=("Arial", 24, "normal"), fill="#cccccc",
                                             text=f"{self.ship_count}")
        self.ship_2 = ShipIcon('images/gun2.gif')
        self.ship_2.goto(-240, -365)
        self.ship_3 = ShipIcon('images/gun.gif')
        self.ship_3.goto(-210, -365)

        winn = explosion.screen
        winn.addshape('images/explosion.gif')
        explosion.shape('images/explosion.gif')
        explosion.penup()
        explosion.hideturtle()

        artist = Artist()
        artist.goto(-345, -350)
        artist.setheading(360)
        artist.pendown()
        artist.pensize(2)
        artist.color("#00dd00")
        artist.forward(690)

    def game_is_over(self):
        game_over = self.cv.create_text(0, -70, text="GAME OVER", font=("Arial", 40, "bold"), fill="#fa0000")


class Ship(Turtle):
    def __init__(self, image_path):
        super().__init__()
        self.t_screen = Screen()
        self.t_screen.addshape(image_path)
        self.shape(image_path)
        # self.hideturtle()
        self.last_dir = NONE
        self.penup()
        self.state = "in_tact"
        self.type = int(image_path[12:13])
        self.value = self.type * 10
        self.missile_speed = 3

    def fire_missile(self):
        my_missile = Missile('alien', (self.xcor(), self.ycor()))
        my_missile.fire()
        missiles.append(my_missile)

    def explode(self):
        global alien_speed, shift, missile_chance
        global destroyed_ships, level_over
        self.hideturtle()
        explosion.goto(self.xcor(), self.ycor())
        explosion.showturtle()
        update_score(self.value)
        sleep(0.15)
        explosion.hideturtle()
        destroyed_ships += 1
        # shift += 1
        if destroyed_ships == 4 * SHIPS_IN_ROW:
            level_over = True
            sleep(0.5)
            level_over = False
            destroyed_ships = 0
            alien_speed += 0.25
            if missile_chance >= 10:
                missile_chance -= 5
            set_ships()


class Missile(Turtle):
    def __init__(self, side, origin):
        super().__init__()
        self.hideturtle()
        self.side = side
        self.t_screen = Screen()
        self.t_screen.addshape('images/missile.gif' if self.side == 'earthling' else 'images/bad_missile.gif')
        self.shape('images/missile.gif' if self.side == 'earthling' else 'images/bad_missile.gif')
        self.color("white")
        self.origin = origin
        self.speed = 0.50 if self.side == 'earthling' else 0.20
        self.setheading(90 if self.side == 'earthling' else 270)
        self.flying = True
        self.penup()

    def fire(self):
        missile_adjust = -35 if self.side == 'earthling' else 35
        self.goto(self.origin[0], self.origin[1] - missile_adjust)
        self.showturtle()
        # while self.flying:

    def move(self):
        global alien_speed, earthling_speed
        self.speed = earthling_speed if self.side == 'earthling' else alien_speed
        self.forward(self.speed)
        if self.side == 'earthling':
            for alien_ship in aliens:
                if alien_ship.isvisible() and alien_ship.distance(self) < 20:
                    self.hideturtle()
                    alien_ship.explode()
                    self.flying = False
                    break
        else:
            if shooter.distance(self) < 20:
                self.hideturtle()
                self.flying = False
                shooter.explode()


class MysteryShip(Turtle):
    def __init__(self):
        super().__init__()
        self.value = randint(3) * 100
        self.color = "#ffffff"
        self.penup()

    def do_run(self):
        pass

    def set_state(self, state):
        pass

    def explode(self):
        pass


class Artist(Turtle):
    def __init__(self):
        super().__init__()
        self.hideturtle()
        self.penup()


def do_missiles():
    global missiles
    while not game_over:
        if level_over:
            sleep(2.0)
        for missile in missiles:
            if missile.ycor() > 355 and missile.side == "earthling":
                missile.hideturtle()
                missiles.remove(missile)
            if missile.ycor() < -355 and missile.side == "alien":
                missile.hideturtle()
                missiles.remove(missile)
            elif missile.flying:
                missile.move()
        # if len(missiles) < 5:
            # sleep(0.5)


def update_score(points):
    current_score = int(gui.cv.itemcget(gui.score, 'text')) + int(points)
    gui.cv.itemconfig(gui.score, text=current_score)
    highscore = int(gui.cv.itemcget(gui.highScore, 'text'))
    if current_score > highscore:
        gui.cv.itemconfig(gui.highScore, text=current_score)
    with open('high_score.txt', 'w') as f:
        f.write(str(current_score))


def move_ships():
    global game_over, missile_chance
    while not game_over:
        if level_over:
            sleep(2.0)
        num = len(aliens) - 1
        while num > -1:
            craft = aliens[num]
            if craft.isvisible() and craft.ycor() <= -284:
                if craft.distance(shooter) < 20:
                    shooter.explode()
            if craft.isvisible() and craft.ycor() < -350:
                craft.explode()

            if not craft.last_dir:
                craft.goto(craft.xcor() + shift, craft.ycor())
                craft.last_dir = RIGHT
            elif craft.last_dir == RIGHT and craft.xcor() < RIGHT_BOUNDS:
                craft.goto(craft.xcor() + shift, craft.ycor())
                craft.last_dir = RIGHT

            elif craft.last_dir == RIGHT and craft.xcor() >= RIGHT_BOUNDS:   # row shift condition
                craft.goto(craft.xcor() - shift, craft.ycor() - 64)
                craft.last_dir = LEFT
                for index in range(num - 1, num - 6, -1):
                    aliens[index].goto(aliens[index].xcor() - shift, aliens[index].ycor() - 64)
                    aliens[index].last_dir = LEFT
                num -= 6
                continue
            elif craft.last_dir == LEFT and craft.xcor() > LEFT_BOUNDS:
                craft.goto(craft.xcor() - shift, craft.ycor())
            elif craft.last_dir == LEFT and craft.xcor() <= LEFT_BOUNDS:   # row shift condition
                craft.goto(craft.xcor() + shift, craft.ycor() - 64)
                craft.last_dir = RIGHT
                try:
                    for index in range(num + 1, num + 6):
                        aliens[index].goto(aliens[index].xcor() + shift, aliens[index].ycor() - 64)
                        aliens[index].last_dir = RIGHT
                except IndexError:
                    print(f"ERROR: line 314 index is {index}")
            if craft.isvisible() and randint(1, missile_chance) == 1:
                if craft.type == 1:
                    craft.fire_missile()
                elif craft.type == 2 and not aliens[num + SHIPS_IN_ROW].isvisible():
                    craft.fire_missile()
                elif craft.type == 3 and num >= 6 and num <= 11 and not aliens[num + SHIPS_IN_ROW].isvisible() \
                        and not aliens[num + (2 * SHIPS_IN_ROW)].isvisible():
                    craft.fire_missile()
                elif craft.type == 3 and num >= 0 and num <= 5 and not aliens[num + SHIPS_IN_ROW].isvisible()\
                        and not aliens[num + (2 * SHIPS_IN_ROW)].isvisible() and not aliens[num + (3 * SHIPS_IN_ROW)].isvisible():
                    craft.fire_missile()
            num -= 1
            sleep(0.01)


shooter = Shooter('images/gun.gif')
screen = Screen()
screen.setup(700, 800)
screen.bgcolor("#000000")
screen.onkeypress(shooter.move_left, "Left")
screen.onkeypress(shooter.move_right, "Right")
screen.onkeypress(shooter.fire_missile, "space")
screen.title("Space Invaders")
screen.tracer(1, 0)
screen.listen()


def set_missiles():
    global alien_missiles
    global earthling_missiles

    for index in range(0, 12):
        alien_missiles.append(Missile('alien', (-400, -400), index))
    for index in range(0, 13):
        earthling_missiles.append(Missile('earthling', (-400, -400), index))


def set_ships():

    corx = -200
    cory = 186

    if len(aliens) == 0:

        for row in [3, 3, 2, 1]:
            for column in range(0, SHIPS_IN_ROW):
                ship = Ship(IMAGE_PATHS[row])
                ship.goto(corx, cory)
                ship.last_x = corx
                ship.showturtle()
                aliens.append(ship)
                corx += 64
                # sleep(1)
            cory -= 64
            corx = -200
    else:
        i = 0
        for row in [3, 3, 2, 1]:
            for column in range(0, SHIPS_IN_ROW):
                alien = aliens[i]
                i += 1
                print(alien)
                alien.goto(corx, cory)
                alien.last_x = corx
                alien.last_dir = None
                alien.showturtle()
                alien.state = ""
                corx += 64
            cory -= 64
            corx = -200


types = []
for ship in aliens:
    types.append(ship.type)

print(types)

gui = GUI()

set_ships()
# set_missiles()
my_thread = threading.Thread(target=move_ships)
my_thread.start()

missile_thread = threading.Thread(target=do_missiles)
missile_thread.start()


screen.exitonclick()
