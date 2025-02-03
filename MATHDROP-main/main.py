import pygame
import random
import time
import os
from fractions import Fraction
import math
pygame.init()
pygame.mixer.init()
coins = 0
unlocked_carts = {"default": True, "gold": False, "teal": False}
selected_cart = "default"
try:
    COIN_IMAGE = pygame.image.load("coin.png")
    COIN_IMAGE = pygame.transform.scale(COIN_IMAGE, (40, 40))
except pygame.error as e:
    print(f"Error loading coin image: {e}")
    COIN_IMAGE = None

try:
    pygame.mixer.music.load("music.mp3")
    pygame.mixer.music.play(-1)
    print("Background music loaded and playing.")
except pygame.error as e:
    print(f"Error loading music: {e}")

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
HIGHLIGHT = (100, 100, 100)
DEFAULT_LIVES = 5
SPEED_INCREMENT = 0.2
LEVEL_UP_THRESHOLD = 7

try:
    FONT = pygame.font.Font("PixelatedEleganceRegular-ovyAA.ttf", 40)
    BUTTON_FONT = pygame.font.Font("PixelatedEleganceRegular-ovyAA.ttf", 28)
except:
    FONT = pygame.font.Font(None, 40)
    BUTTON_FONT = pygame.font.Font(None, 28)

BACKGROUND_IMAGES = {
    "menu": "backgrounds/menu_background.png",
    1: "backgrounds/istockphoto-1333010525-612x612.jpg",
    2: "backgrounds/background_level_1.jpg",
    3: "backgrounds/yrkGs9.png"
}
def load_background(level):
    try:
        return pygame.transform.scale(pygame.image.load(BACKGROUND_IMAGES[level]), (WIDTH, HEIGHT))
    except:
        return None
class Button:
    def __init__(self, text, x, y, width, height):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = GRAY

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
        text_surface = BUTTON_FONT.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Math Drop")

game_state = "menu"
score = 0
lives = DEFAULT_LIVES
current_level = 1
fall_speed = 3
cart_width = 100
cart_height = 40
minecart = pygame.Rect(WIDTH // 2 - cart_width // 2, HEIGHT - 80, cart_width, cart_height)
answer_positions = []
def run_slot_machine():
    global coins, unlocked_carts
    if coins < 10:
        print("Not enough coins!")
        return None

    coins -= 10
    result = random.randint(1, 250)
    if result == 1:
        unlocked_carts["teal"] = True
        print("Diamond Cart Unlocked!")
        return "teal"
    elif result <= 5:
        unlocked_carts["gold"] = True
        print("Golden Cart Unlocked!")
        return "gold"
    else:
        print("No unlock! Try again.")
        return None

def gcd(a, b):
    return math.gcd(a, b)

def generate_problem(level):
    """Generates math problems based on the level."""
    if level == 1:
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        op = random.choice(['+', '-', '*'])
        problem = f"{num1} {op} {num2}"
        correct_answer = eval(problem)

    elif level == 2:
        if random.random() < 0.5:
            num1, denom1 = random.randint(1, 5), random.randint(2, 6)
            num2, denom2 = random.randint(1, 5), random.randint(2, 6)

            while denom1 != denom2 or num1 == denom1 or num2 == denom2:
                num1, denom1 = random.randint(1, 5), random.randint(2, 6)
                num2, denom2 = random.randint(1, 5), random.randint(2, 6)

            fraction1 = Fraction(num1, denom1)
            fraction2 = Fraction(num2, denom2)

            op = random.choice(['+', '-'])

            fractionAns = fraction1 + fraction2 if op == '+' else fraction1 - fraction2
            fractionAns = fractionAns.limit_denominator()

            problem = f"{fraction1} {op} {fraction2}"
            correct_answer = fractionAns

        else:
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            op = random.choice(['+', '-', '*'])
            problem = f"{num1} {op} {num2}"
            correct_answer = eval(problem)

    elif level == 3:
        if random.random() < 0.5:
            num = random.choice([4, 9, 16, 25, 36, 49, 64, 81, 100])
            problem = f"√{num}"
            correct_answer = int(math.sqrt(num))
        elif random.random() < 0.5:
            num = random.randint(2, 10)
            problem = f"{num}^2"
            correct_answer = num ** 2
        else:
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            op = random.choice(['+', '-', '*'])
            problem = f"{num1} {op} {num2}"
            correct_answer = Fraction(eval(problem)).limit_denominator()

    answers = [correct_answer]

    if isinstance(correct_answer, Fraction):
        for _ in range(3):
            incorrect_num = random.randint(1, 10)
            incorrect_den = random.randint(1, 10)
            while incorrect_den == 0:
                incorrect_den = random.randint(1, 10)
            answers.append(Fraction(incorrect_num, incorrect_den).limit_denominator())
    else:
        answers += [random.randint(1, 100) for _ in range(3)]

    random.shuffle(answers)
    return problem, correct_answer, answers
SHOP_BACKGROUND = pygame.transform.scale(pygame.image.load("smithster.png"), (WIDTH, HEIGHT))

def shop_menu():
    global game_state, selected_cart, unlocked_carts, coins

    buttons = [
        Button("Play Slot (10 Coins)", WIDTH // 2 - 175, 200, 350, 50),
        Button("Select Default Cart", WIDTH // 2 - 225, 300, 450, 50),
        Button("Select Golden Cart", WIDTH // 2 - 225, 400, 450, 50),
        Button("Select Diamond Cart", WIDTH // 2 - 225, 500, 450, 50),
        Button("Back", WIDTH // 2 - 60, 600, 120, 45),
    ]

    exit_button = Button("Exit", WIDTH - 110, 10, 100, 40)

    # Feedback message system
    feedback_message = ""
    message_timer = 0

    while game_state == "shop":
        screen.blit(SHOP_BACKGROUND, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        title_surface = FONT.render("SHOP", True, WHITE)
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 100))

        if COIN_IMAGE:
            screen.blit(COIN_IMAGE, (WIDTH - 100, HEIGHT - 60))
        coin_count_text = FONT.render(str(coins), True, WHITE)
        screen.blit(coin_count_text, (WIDTH - 50, HEIGHT - 50))

        # Render 
        if feedback_message:
            feedback_bg_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT - 150, 400, 50)
            pygame.draw.rect(screen, WHITE, feedback_bg_rect)
            pygame.draw.rect(screen, BLACK, feedback_bg_rect, 2)

            feedback_surface = BUTTON_FONT.render(feedback_message, True, BLACK)
            screen.blit(feedback_surface,
                        (WIDTH // 2 - feedback_surface.get_width() // 2, HEIGHT - 140))
            message_timer += 1
            if message_timer > 180:  
                feedback_message = ""
                message_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:  
                for button in buttons:
                    if button.is_hovered(mouse_pos):  
                        if button.text == "Play Slot (10 Coins)":
                            if coins < 10:
                                feedback_message = "Not enough coins!"  
                            else:
                                result = run_slot_machine()
                                if result:
                                    unlocked_carts[result] = True  
                                    feedback_message = f"{result.capitalize()} Cart Unlocked!"
                                else:
                                    feedback_message = "No unlock! Try again."

                        elif button.text.startswith("Select"):  
                            cart_color = button.text.split()[-2].lower()  
                            if unlocked_carts.get(cart_color, False):  
                                selected_cart = cart_color  
                                feedback_message = f"{cart_color.capitalize()} Cart Selected!"
                            else:
                                feedback_message = f"This {cart_color.capitalize()} Cart is locked!"

                        elif button.text == "Back":  
                            game_state = "menu"
                            return

                # Handle Exit button click (return to main menu)
                if exit_button.is_hovered(mouse_pos):
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left mouse button
                            game_state = "menu"
                            return

        # Render buttons
        for button in buttons:
            # Dynamically highlight "Select" buttons based on unlock status
            if button.text.startswith("Select"):
                cart_color = button.text.split()[-2].lower()
                button.color = HIGHLIGHT if unlocked_carts.get(cart_color, False) else GRAY
            button.color = HIGHLIGHT if button.is_hovered(mouse_pos) else GRAY
            button.draw(screen)

        # Render the Exit button
        exit_button.color = HIGHLIGHT if exit_button.is_hovered(mouse_pos) else GRAY
        exit_button.draw(screen)

        # Update the screen
        pygame.display.flip()


def shop_page(screen, coins, unlocked_carts, selected_cart):
    """Renders the shop page and handles purchasing and equipping minecarts."""
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GOLD = (255, 215, 0)
    TEAL = (0, 128, 128)
    GRAY = (200, 200, 200)
    GREEN = (0, 255, 0)

    # Sizes and Positions
    screen_width, screen_height = screen.get_size()
    # Rectangles on the left for GOLD and TEAL
    gold_cart_rect = pygame.Rect(screen_width // 6, screen_height // 4, 100, 100)
    teal_cart_rect = pygame.Rect(screen_width // 6, screen_height // 2, 100, 100)

    # "Buy" or "Equip" buttons on the right of the minecart boxes
    button_width, button_height = 120, 40
    gold_button_rect = pygame.Rect(screen_width // 2, gold_cart_rect.y + 30, button_width, button_height)
    teal_button_rect = pygame.Rect(screen_width // 2, teal_cart_rect.y + 30, button_width, button_height)

    # Fonts
    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 48)

    running = True
    while running:
        screen.fill(WHITE)

        # Title
        title_text = title_font.render("Minecart Shop", True, BLACK)
        title_rect = title_text.get_rect(center=(screen_width // 2, 50))
        screen.blit(title_text, title_rect)

        # Display coins
        coins_text = font.render(f"Coins: {coins}", True, BLACK)
        coins_rect = coins_text.get_rect(topleft=(20, 20))
        screen.blit(coins_text, coins_rect)

        # Draw Gold Cart Box
        pygame.draw.rect(screen, GOLD, gold_cart_rect)
        gold_text = font.render("Gold Cart", True, BLACK)
        gold_text_rect = gold_text.get_rect(center=gold_cart_rect.center)
        screen.blit(gold_text, gold_text_rect)

        # Draw Teal Cart Box
        pygame.draw.rect(screen, TEAL, teal_cart_rect)
        teal_text = font.render("Teal Cart", True, BLACK)
        teal_text_rect = teal_text.get_rect(center=teal_cart_rect.center)
        screen.blit(teal_text, teal_text_rect)

        # Draw buttons
        def draw_button(rect, text, color=GRAY):
            pygame.draw.rect(screen, color, rect)
            button_text = font.render(text, True, BLACK)
            button_text_rect = button_text.get_rect(center=rect.center)
            screen.blit(button_text, button_text_rect)

        gold_button_text = ("Buy" if "gold" not in unlocked_carts else
                            ("Equip" if selected_cart != "gold" else "Equipped"))
        gold_button_color = GRAY if "gold" not in unlocked_carts else (GREEN if selected_cart == "gold" else GOLD)
        draw_button(gold_button_rect, gold_button_text, gold_button_color)

        teal_button_text = ("Buy" if "teal" not in unlocked_carts else
                            ("Equip" if selected_cart != "teal" else "Equipped"))
        teal_button_color = GRAY if "teal" not in unlocked_carts else (GREEN if selected_cart == "teal" else TEAL)
        draw_button(teal_button_rect, teal_button_text, teal_button_color)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if gold_button_rect.collidepoint(event.pos):
                        if "gold" not in unlocked_carts and coins >= 50:
                            coins -= 50
                            unlocked_carts.append("gold")
                        elif "gold" in unlocked_carts:
                            selected_cart = "gold"

                    if teal_button_rect.collidepoint(event.pos):
                        if "teal" not in unlocked_carts and coins >= 250:
                            coins -= 250
                            unlocked_carts.append("teal")
                        elif "teal" in unlocked_carts:
                            selected_cart = "teal"

        pygame.display.flip()
    return coins, unlocked_carts, selected_cart



def show_level_text(level):
    """Displays level transition text."""
    screen.fill(BLACK)
    text = FONT.render(f"LEVEL {level}", True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 20))
    pygame.display.update()
    time.sleep(2)
def get_negative_color(color):
    """Returns the negative (inverted) color."""
    return (255 - color[0], 255 - color[1], 255 - color[2])
def draw_game():
    """Draws the game screen."""
    screen.fill(WHITE)
    text_color = WHITE

    if BACKGROUND:
        screen.blit(BACKGROUND, (0, 0))
        try:
            avg_color = pygame.transform.average_color(BACKGROUND)
            text_color = get_negative_color(avg_color)
        except Exception as e:
            print(f"Error calculating average background color: {e}")
            text_color = BLACK

    text = FONT.render(problem, True, text_color)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 70))

    score_text = FONT.render(f"Score: {score} Lives: {lives} Level: {current_level}", True, text_color)
    screen.blit(score_text, (20, 20))

    for i, ans in enumerate(answers):
        pygame.draw.circle(screen, GRAY, (answer_positions[i].x + 30, answer_positions[i].y + 30), 30)
        ans_text = FONT.render(str(ans), True, WHITE)
        screen.blit(ans_text, (answer_positions[i].x + 30 - ans_text.get_width() // 2, answer_positions[i].y + 20))

    pygame.draw.rect(screen, HIGHLIGHT, minecart)

    if COIN_IMAGE:
        screen.blit(COIN_IMAGE, (WIDTH - 100, HEIGHT - 60))
    coin_count_text = FONT.render(str(coins), True, WHITE)
    screen.blit(coin_count_text, (WIDTH - 50, HEIGHT - 50))

    pygame.display.update()

def singleplayer_mode():
    """Handles the singleplayer game loop with proper level progression."""
    global game_state, problem, correct_answer, answers, score, lives, answer_positions, fall_speed, current_level, BACKGROUND, coins

    score = 0
    lives = DEFAULT_LIVES
    fall_speed = 3
    current_level = 1

    while current_level <= 3:
        BACKGROUND = load_background(current_level)
        show_level_text(current_level)

        problem, correct_answer, answers = generate_problem(current_level)
        answer_positions = [pygame.Rect(WIDTH // 5 * (i + 1) - 30, 200, 60, 60) for i in range(4)]

        level_running = True
        while level_running:
            pygame.time.delay(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            keys = pygame.key.get_pressed()
            if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and minecart.x > 0:
                minecart.x -= 20
            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and minecart.x < WIDTH - cart_width:
                minecart.x += 20

            for rect in answer_positions:
                rect.y += fall_speed
                if rect.y > HEIGHT:
                    lives -= 1
                    rect.y = 200
                    problem, correct_answer, answers = generate_problem(current_level)
                    for i in range(4):
                        answer_positions[i].y = 200
                    if lives <= 0:
                        game_state = "menu"
                        return

            for i, rect in enumerate(answer_positions):
                if minecart.colliderect(rect):
                    if answers[i] == correct_answer:
                        score += 1
                        coins += 1
                        fall_speed += SPEED_INCREMENT
                    else:
                        lives -= 1
                    problem, correct_answer, answers = generate_problem(current_level)
                    for i in range(4):
                        answer_positions[i].y = 200

                    if lives <= 0:
                        game_state = "menu"
                        return

            if fall_speed >= LEVEL_UP_THRESHOLD:
                current_level += 1
                if current_level > 1:
                    lives += 2
                level_running = False
                fall_speed = 3

            draw_game()

    game_state = "menu"

def main_menu():
    global game_state, BACKGROUND
    BACKGROUND = load_background("menu")

    buttons = [
        Button("Singleplayer", WIDTH // 2 - 110, 220, 240, 50),
        Button("Shop", WIDTH // 2 - 90, 340, 180, 45),
        Button("Credits", WIDTH // 2 - 90, 400, 180, 45),
    ]

    while game_state == "menu":
        screen.fill(BLACK)
        if BACKGROUND:
            screen.blit(BACKGROUND, (0, 0))

        title_surface = FONT.render("MATH DROP", True, WHITE)
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 100))

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    if button.is_hovered(mouse_pos):
                        if button.text == "Singleplayer":
                            game_state = "singleplayer"
                            singleplayer_mode()
                        elif button.text == "Shop":
                            game_state = "shop"
                            shop_menu()
                        elif button.text == "Credits":
                            print("Credits Screen Coming Soon!")

        for button in buttons:
            button.color = HIGHLIGHT if button.is_hovered(mouse_pos) else GRAY
            button.draw(screen)

        pygame.display.flip()

while True:
    main_menu()