import pygame
from game import *

# GLOBALS
display = None
game = None
clock = pygame.time.Clock()

# COLORS
green = (0, 255, 0)
blue = (0, 0, 255)
red = (255, 0, 0)
grey = (127, 127, 127)
black = (0, 0, 0)
white = (255, 255, 255)
yellow = (255, 255, 0)

# VARIABLES
display_tiles = [64, 32, 16, 8, 4, 2, 1]
tile_size = [8, 16, 32, 64, 128, 256, 512]
max_zoom_level = 7
current_zoom_level = 2
bar_size = 20
total_tiles = 100
game_speed = 25
info_column_size = 250
info_height = 25
scroll_speed = 1
control_column_size = 100
button_height = 25
display_map_size = display_tiles[current_zoom_level] * tile_size[current_zoom_level] + bar_size
button_x_start = display_map_size + info_column_size
button_x_end = display_map_size + info_column_size + control_column_size
pause_y_start = 0
pause_y_end = button_height
save_y_start = button_height
save_y_end = button_height * 2
load_y_start = button_height * 2
load_y_end = button_height * 3
screen_size = (display_map_size + info_column_size + control_column_size, display_map_size)


def main():
    pygame.font.init()
    setup()
    while not game.exit:
        loop()
    pygame.quit()
    quit()


def loop():
    global game
    game.tick()
    event_handle()
    draw()
    clock.tick(game_speed)


def event_handle():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game.exit = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_event(event)

    keys = pygame.key.get_pressed()
    keys_pressed(keys)


def mouse_event(event):
    global current_zoom_level
    if event.button == 1:
        mouse_button_press(event)
    elif event.button == 4:
        if current_zoom_level != max_zoom_level - 1:
            current_zoom_level += 1
    elif event.button == 5:
        if current_zoom_level != 0:
            current_zoom_level -= 1
            # Makes sure that when zooming out, map does not go out of range
            if game.current_display[0] > game.size - display_tiles[current_zoom_level]:
                game.current_display[0] = game.size - display_tiles[current_zoom_level]
            if game.current_display[1] > game.size - display_tiles[current_zoom_level]:
                game.current_display[1] = game.size - display_tiles[current_zoom_level]


def mouse_button_press(event):
    x, y = event.pos
    if pause_pressed(x, y):
        game.paused = not game.paused
    elif save_pressed(x, y):
        game.save()
    elif load_pressed(x, y):
        game.load()


def pause_pressed(x, y):
    if x < button_x_start or x > button_x_end or y < pause_y_start or y > pause_y_end:
        return False
    return True


def save_pressed(x, y):
    if x < button_x_start or x > button_x_end or y < save_y_start or y > save_y_end:
        return False
    return True


def load_pressed(x, y):
    if x < button_x_start or x > button_x_end or y < load_y_start or y > load_y_end:
        return False
    return True


def keys_pressed(keys):
    if game.time_passed % scroll_speed == 0:
        # Vertical movement
        if not (keys[pygame.K_UP] and keys[pygame.K_DOWN]):
            if keys[pygame.K_UP]:
                if game.current_display[1] != 0:
                    game.current_display[1] -= 1
            elif keys[pygame.K_DOWN]:
                if game.current_display[1] != total_tiles - display_tiles[current_zoom_level]:
                    game.current_display[1] += 1

        # Horizontal movement
        if not (keys[pygame.K_LEFT] and keys[pygame.K_RIGHT]):
            if keys[pygame.K_LEFT]:
                if game.current_display[0] != 0:
                    game.current_display[0] -= 1
            elif keys[pygame.K_RIGHT]:
                if game.current_display[0] != total_tiles - display_tiles[current_zoom_level]:
                    game.current_display[0] += 1


def draw():
    display.fill(black)

    draw_bars()

    draw_tiles()

    draw_entities()

    draw_info()

    draw_controls()

    pygame.display.update()


def draw_controls():

    draw_pause()

    draw_save()

    draw_load()


def draw_pause():
    display.fill(blue, rect=[button_x_start, pause_y_start, control_column_size, button_height])
    font = pygame.font.SysFont(None, button_height)
    text_str = "Pause"
    if game.paused:
        text_str = "Unpause"
    text = font.render(text_str, True, black)
    display.blit(text, [button_x_start, pause_y_start])


def draw_save():
    display.fill(green, rect=[button_x_start, save_y_start, control_column_size, button_height])
    font = pygame.font.SysFont(None, button_height)
    text_str = "Save"
    text = font.render(text_str, True, black)
    display.blit(text, [button_x_start, save_y_start])


def draw_load():
    display.fill(blue, rect=[button_x_start, load_y_start, control_column_size, button_height])
    font = pygame.font.SysFont(None, button_height)
    text_str = "Load"
    text = font.render(text_str, True, black)
    display.blit(text, [button_x_start, load_y_start])


def draw_bars():
    display.fill(white, rect=[0, 0, display_map_size, bar_size])
    display.fill(white, rect=[0, 0, bar_size, display_map_size])
    font = pygame.font.SysFont(None, 15)
    type_horizontal_scale(font)
    type_vertical_scale(font)


def type_horizontal_scale(font):
    for i in range(1, display_tiles[current_zoom_level]):
        vertical_shift = 0
        if i % 2 == 0:
            vertical_shift = bar_size // 2
        text_str = str(game.current_display[0] + i)
        text = font.render(text_str, True, red)
        display.blit(text, [bar_size + i*tile_size[current_zoom_level], vertical_shift])


def type_vertical_scale(font):
    for i in range(1, display_tiles[current_zoom_level]):
        text_str = str(game.current_display[1] + i)
        text = font.render(text_str, True, red)
        display.blit(text, [0, bar_size + i*tile_size[current_zoom_level]])


def draw_tiles():
    max_food = game.max_food()
    for i in range(game.current_display[0], game.current_display[0] + display_tiles[current_zoom_level]):
        for j in range(game.current_display[1], game.current_display[1] + display_tiles[current_zoom_level]):
            hue = int(game.tiles[i][j].food / max_food * 255)
            x = i - game.current_display[0]
            y = j - game.current_display[1]
            display.fill((0, hue, 0), rect=[bar_size + x * tile_size[current_zoom_level], bar_size + y * tile_size[current_zoom_level], tile_size[current_zoom_level], tile_size[current_zoom_level]])


def draw_entities():
    for entity in game.entities:
        for body in entity.bodies:
            if game.current_display[0] < body.location[0] < game.current_display[0] + display_tiles[current_zoom_level] and game.current_display[1] < body.location[1] < game.current_display[1] + display_tiles[current_zoom_level]:
                x_pos = int((body.location[0] - game.current_display[0]) * tile_size[current_zoom_level] + bar_size)
                y_pos = int((body.location[1] - game.current_display[1]) * tile_size[current_zoom_level] + bar_size)
                body_size = int(body.size * tile_size[current_zoom_level])
                mouth_size = int(body.mouth_size * tile_size[current_zoom_level])
                pygame.draw.circle(display, black, [x_pos, y_pos], body_size)
                pygame.draw.circle(display, blue, [x_pos, y_pos], mouth_size)


def type_info(info_type, info, info_id, font):
    text_str = info_type + ": " + info
    text = font.render(text_str, True, green)
    display.blit(text, [display_map_size, info_id*info_height])


def draw_info():
    # Displays time passed
    font = pygame.font.SysFont(None, 25)
    hours = str(game.time_passed // 360000)
    minutes = str((game.time_passed % 360000) // 6000)
    seconds = str((game.time_passed % 6000) // 100)
    ticks = str(game.time_passed % 100)
    max_food = str(int(game.max_food()))

    type_info("Hours", hours, 0, font)
    type_info("Minutes", minutes, 1, font)
    type_info("Seconds", seconds, 2, font)
    type_info("Ticks", ticks, 3, font)
    type_info("Max food", max_food, 4, font)


def setup():
    global display
    global game
    pygame.init()
    game = Game(total_tiles)
    display = pygame.display.set_mode(screen_size)


main()
