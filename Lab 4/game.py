import pygame

import random

from collections import deque



# =============================================================

# SETTINGS

# =============================================================



TILE = 40

COLS, ROWS = 20, 15



WALL, FLOOR, CHEST, KEY, TRAP = 0, 1, 2, 3, 4



SPEED = 3

NUM_TRAPS = 8



WIDTH = COLS * TILE

HEIGHT = ROWS * TILE + 50

FPS = 60



# Mini-map

MINIMAP_CELL = 6

MINIMAP_WIDTH = COLS * MINIMAP_CELL

MINIMAP_HEIGHT = ROWS * MINIMAP_CELL

MINIMAP_MARGIN = 10

# Task 4: Inventory UI
INVENTORY_SLOT_SIZE = 36
INVENTORY_MARGIN = 8





# =============================================================

# COLORS

# =============================================================



COLORS = {

    WALL: (60, 50, 70),

    FLOOR: (200, 190, 170),

    CHEST: (200, 160, 30),

    KEY: (220, 220, 60),

    TRAP: (180, 40, 40),

}





# =============================================================

# FIND PATH

# =============================================================



def find_path(grid, start, goal):



    if start is None or goal is None:

        return set()



    queue = deque([start])

    previous = {start: None}



    while queue:



        current = queue.popleft()



        if current == goal:

            break



        c, r = current



        neighbors = [

            (c + 1, r),

            (c - 1, r),

            (c, r + 1),

            (c, r - 1)

        ]



        for nc, nr in neighbors:



            if not (0 <= nc < COLS and 0 <= nr < ROWS):

                continue



            if grid[nr][nc] == WALL:

                continue



            if (nc, nr) in previous:

                continue



            previous[(nc, nr)] = current

            queue.append((nc, nr))



    if goal not in previous:

        return set()



    path = set()

    current = goal



    while current is not None:

        path.add(current)

        current = previous[current]



    return path





# =============================================================

# DUNGEON GENERATION

# =============================================================



def generate_world():



    grid = [[WALL] * COLS for _ in range(ROWS)]

    rooms = []



    # Generate rooms

    for _ in range(8):



        w = random.randint(3, 6)

        h = random.randint(3, 5)



        x = random.randint(1, COLS - w - 1)

        y = random.randint(1, ROWS - h - 1)



        room = pygame.Rect(x, y, w, h)



        overlap = any(

            room.inflate(2, 2).colliderect(r)

            for r in rooms

        )



        if not overlap:



            rooms.append(room)



            for ry in range(y, y + h):

                for rx in range(x, x + w):

                    grid[ry][rx] = FLOOR



    # Connect rooms

    for i in range(len(rooms) - 1):



        ax, ay = rooms[i].centerx, rooms[i].centery

        bx, by = rooms[i + 1].centerx, rooms[i + 1].centery



        cx = ax



        while cx != bx:



            grid[ay][cx] = FLOOR



            if bx > cx:

                cx += 1

            else:

                cx -= 1



        cy = ay



        while cy != by:



            grid[cy][bx] = FLOOR



            if by > cy:

                cy += 1

            else:

                cy -= 1



    # Place key and chest

    key_position = None

    chest_position = None



    if len(rooms) >= 2:



        chest_room = rooms[-1]

        key_room = rooms[-2]



        chest_position = (

            chest_room.centerx,

            chest_room.centery

        )



        key_position = (

            key_room.centerx,

            key_room.centery

        )



        grid[

            chest_position[1]

        ][

            chest_position[0]

        ] = CHEST



        grid[

            key_position[1]

        ][

            key_position[0]

        ] = KEY



    start = rooms[0] if rooms else None



    # =========================================================

    # TASK 1: TRAPS

    # Keep guaranteed route safe:

    # START -> KEY -> CHEST

    # =========================================================



    safe_path = set()



    if start and key_position:



        start_position = (

            start.centerx,

            start.centery

        )



        safe_path.update(

            find_path(

                grid,

                start_position,

                key_position

            )

        )



    if key_position and chest_position:



        safe_path.update(

            find_path(

                grid,

                key_position,

                chest_position

            )

        )



    trap_candidates = []



    for r in range(ROWS):



        for c in range(COLS):



            if grid[r][c] != FLOOR:

                continue



            if (c, r) in safe_path:

                continue



            if start and start.collidepoint(c, r):

                continue



            trap_candidates.append((r, c))



    random.shuffle(trap_candidates)



    for r, c in trap_candidates[:NUM_TRAPS]:

        grid[r][c] = TRAP



    return grid, start





# =============================================================

# PLAYER

# =============================================================



class Player:



    def __init__(self, x, y):



        self.rect = pygame.Rect(

            x, y, 28, 28

        )



        self.color = (60, 120, 220)

        self.has_key = False



    def move(self, keys, grid, rows, cols):



        dx = 0

        dy = 0



        if keys[pygame.K_LEFT] or keys[pygame.K_a]:

            dx = -SPEED



        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:

            dx = SPEED



        if keys[pygame.K_UP] or keys[pygame.K_w]:

            dy = -SPEED



        if keys[pygame.K_DOWN] or keys[pygame.K_s]:

            dy = SPEED



        self._try_move(dx, 0, grid, rows, cols)

        self._try_move(0, dy, grid, rows, cols)



    def _try_move(self, dx, dy, grid, rows, cols):



        new = self.rect.move(dx, dy)



        corners = [

            (new.left, new.top),

            (new.right - 1, new.top),

            (new.left, new.bottom - 1),

            (new.right - 1, new.bottom - 1)

        ]



        for px, py in corners:



            c = px // TILE

            r = py // TILE



            if (

                not (0 <= r < rows and 0 <= c < cols)

                or grid[r][c] == WALL

            ):

                return



        self.rect = new



    def draw(self, screen):



        pygame.draw.ellipse(

            screen,

            self.color,

            self.rect

        )



        if self.has_key:



            pygame.draw.circle(

                screen,

                (220, 220, 60),

                (

                    self.rect.right - 6,

                    self.rect.top + 6

                ),

                5

            )





# =============================================================

# TASK 2: GUARD

# =============================================================



class Guard:



    def __init__(self, point1, point2):



        self.point1 = pygame.Vector2(point1)

        self.point2 = pygame.Vector2(point2)



        # Start exactly at point1

        self.position = pygame.Vector2(point1)



        self.rect = pygame.Rect(

            round(self.position.x),

            round(self.position.y),

            28,

            28

        )



        # Slightly faster so movement is obvious

        self.speed = 2



        self.direction = 1



        self.color = (190, 60, 60)



    def update(self):



        # Continuously switch between the two points

        if self.direction == 1:

            target = self.point2

        else:

            target = self.point1



        movement = target - self.position

        distance = movement.length()



        if distance <= self.speed:



            # Arrived at patrol point

            self.position = pygame.Vector2(target)



            # Immediately reverse direction

            self.direction *= -1



        else:



            # Move toward target every frame

            self.position += (

                movement.normalize()

                * self.speed

            )



        self.rect.topleft = (

            round(self.position.x),

            round(self.position.y)

        )



    def draw(self, screen):



        pygame.draw.rect(

            screen,

            self.color,

            self.rect,

            border_radius=6

        )



        pygame.draw.circle(

            screen,

            (255, 255, 255),

            (

                self.rect.left + 8,

                self.rect.top + 9

            ),

            3

        )



        pygame.draw.circle(

            screen,

            (255, 255, 255),

            (

                self.rect.right - 8,

                self.rect.top + 9

            ),

            3

        )





# =============================================================

# GAME ENGINE

# =============================================================



class GameEngine:



    def __init__(self):



        pygame.init()



        self.screen = pygame.display.set_mode(

            (WIDTH, HEIGHT)

        )



        pygame.display.set_caption(

            "Treasure Hunt"

        )



        self.clock = pygame.time.Clock()



        self.font = pygame.font.SysFont(

            "monospace",

            24

        )



        self.big_font = pygame.font.SysFont(

            "monospace",

            40,

            bold=True

        )



        self.reset()



    # =========================================================

    # RESET

    # =========================================================



    def reset(self):



        self.grid, start = generate_world()



        if start:



            self.start_x = start.x * TILE + 6

            self.start_y = start.y * TILE + 6



        else:



            self.start_x = TILE + 6

            self.start_y = TILE + 6



        self.player = Player(

            self.start_x,

            self.start_y

        )



        # =====================================================

        # Find chest

        # =====================================================



        chest_position = None



        for r in range(ROWS):



            for c in range(COLS):



                if self.grid[r][c] == CHEST:



                    chest_position = (c, r)

                    break



            if chest_position:

                break



        # =====================================================

        # TASK 2: Create continuous patrol near chest

        # =====================================================



        if chest_position:



            chest_col, chest_row = chest_position



            # Find floor cells on the same row near chest

            same_row = []



            for c in range(COLS):



                if self.grid[chest_row][c] == FLOOR:



                    distance = abs(

                        c - chest_col

                    )



                    if distance <= 4:

                        same_row.append(c)



            # Need two genuinely different patrol points

            if len(same_row) >= 2:



                left_col = min(same_row)

                right_col = max(same_row)



                point1 = (

                    left_col * TILE + 6,

                    chest_row * TILE + 6

                )



                point2 = (

                    right_col * TILE + 6,

                    chest_row * TILE + 6

                )



            else:



                # Try vertical patrol near chest

                same_col = []



                for r in range(ROWS):



                    if self.grid[r][chest_col] == FLOOR:



                        distance = abs(

                            r - chest_row

                        )



                        if distance <= 4:

                            same_col.append(r)



                if len(same_col) >= 2:



                    top_row = min(same_col)

                    bottom_row = max(same_col)



                    point1 = (

                        chest_col * TILE + 6,

                        top_row * TILE + 6

                    )



                    point2 = (

                        chest_col * TILE + 6,

                        bottom_row * TILE + 6

                    )



                else:



                    # Final fallback:

                    # create a guaranteed 2-cell horizontal patrol

                    # around the chest area.

                    point1 = (

                        max(1, chest_col - 1)

                        * TILE + 6,

                        chest_row * TILE + 6

                    )



                    point2 = (

                        min(COLS - 2, chest_col + 1)

                        * TILE + 6,

                        chest_row * TILE + 6

                    )



            self.guard = Guard(

                point1,

                point2

            )



        else:



            # Safety fallback

            center = (

                WIDTH // 2,

                ROWS * TILE // 2

            )



            self.guard = Guard(

                (

                    center[0] - TILE,

                    center[1]

                ),

                (

                    center[0] + TILE,

                    center[1]

                )

            )



        self.won = False



        self.status = (

            "Find the KEY, then the CHEST!"

        )



    # =========================================================

    # PLAYER RESET ONLY

    # =========================================================



    def reset_player_to_start(self):



        self.player.rect.topleft = (

            self.start_x,

            self.start_y

        )



    # =========================================================

    # EVENTS

    # =========================================================



    def handle_events(self):



        for event in pygame.event.get():



            if event.type == pygame.QUIT:

                return False



            if (

                event.type == pygame.KEYDOWN

                and event.key == pygame.K_r

            ):



                self.reset()



        return True



    # =========================================================

    # UPDATE

    # =========================================================



    def update(self):



        if self.won:

            return



        # Player movement

        keys = pygame.key.get_pressed()



        self.player.move(

            keys,

            self.grid,

            ROWS,

            COLS

        )



        # =====================================================

        # TASK 2: Guard moves EVERY frame

        # =====================================================



        self.guard.update()



        # Guard collision

        if self.player.rect.colliderect(

            self.guard.rect

        ):



            self.reset_player_to_start()



            self.status = (

                "Guard caught you! Back to start!"

            )



        # =====================================================

        # TASK 1: Trap / Key / Chest

        # =====================================================



        player_row = (

            self.player.rect.centery // TILE

        )



        player_col = (

            self.player.rect.centerx // TILE

        )



        if (

            0 <= player_row < ROWS

            and 0 <= player_col < COLS

        ):



            cell = self.grid[

                player_row

            ][

                player_col

            ]



            # Trap

            if cell == TRAP:



                self.reset_player_to_start()



                self.status = (

                    "Trap! Back to start!"

                )



            # Key

            elif cell == KEY:



                self.player.has_key = True



                self.grid[

                    player_row

                ][

                    player_col

                ] = FLOOR



                self.status = (

                    "Got the key! Find the CHEST!"

                )



            # Chest

            elif (

                cell == CHEST

                and self.player.has_key

            ):



                self.won = True



                self.status = (

                    "Treasure found!"

                )



    # =========================================================

    # TASK 3: MINI-MAP

    # =========================================================



    def draw_minimap(self):



        map_x = (

            WIDTH

            - MINIMAP_WIDTH

            - MINIMAP_MARGIN

        )



        map_y = MINIMAP_MARGIN



        panel = pygame.Rect(

            map_x - 4,

            map_y - 4,

            MINIMAP_WIDTH + 8,

            MINIMAP_HEIGHT + 8

        )



        pygame.draw.rect(

            self.screen,

            (10, 10, 15),

            panel

        )



        # Actual dungeon grid

        for r in range(ROWS):



            for c in range(COLS):



                cell = self.grid[r][c]



                mini_rect = pygame.Rect(

                    map_x + c * MINIMAP_CELL,

                    map_y + r * MINIMAP_CELL,

                    MINIMAP_CELL,

                    MINIMAP_CELL

                )



                if cell == WALL:



                    color = (

                        35,

                        30,

                        45

                    )



                elif cell == FLOOR:



                    color = (

                        180,

                        175,

                        160

                    )



                elif cell == KEY:



                    color = (

                        255,

                        220,

                        40

                    )



                elif cell == CHEST:



                    color = (

                        180,

                        110,

                        20

                    )



                elif cell == TRAP:



                    color = (

                        220,

                        50,

                        50

                    )



                else:



                    color = (

                        100,

                        100,

                        100

                    )



                pygame.draw.rect(

                    self.screen,

                    color,

                    mini_rect

                )



        # Player marker

        player_col = (

            self.player.rect.centerx // TILE

        )



        player_row = (

            self.player.rect.centery // TILE

        )



        if (

            0 <= player_col < COLS

            and

            0 <= player_row < ROWS

        ):



            player_rect = pygame.Rect(

                map_x + player_col * MINIMAP_CELL,

                map_y + player_row * MINIMAP_CELL,

                MINIMAP_CELL,

                MINIMAP_CELL

            )



            pygame.draw.rect(

                self.screen,

                (40, 120, 255),

                player_rect

            )



        # Guard marker

        guard_col = (

            self.guard.rect.centerx // TILE

        )



        guard_row = (

            self.guard.rect.centery // TILE

        )



        if (

            0 <= guard_col < COLS

            and

            0 <= guard_row < ROWS

        ):



            guard_rect = pygame.Rect(

                map_x + guard_col * MINIMAP_CELL,

                map_y + guard_row * MINIMAP_CELL,

                MINIMAP_CELL,

                MINIMAP_CELL

            )



            pygame.draw.rect(

                self.screen,

                (255, 100, 100),

                guard_rect

            )



        # Border

        pygame.draw.rect(

            self.screen,

            (230, 230, 230),

            panel,

            1

        )



    # =========================================================

    # DRAW

    # =========================================================



    # =========================================================
    # TASK 4: INVENTORY UI
    # =========================================================

    def draw_inventory(self):

        slot_x = WIDTH - INVENTORY_SLOT_SIZE - INVENTORY_MARGIN
        slot_y = ROWS * TILE + (50 - INVENTORY_SLOT_SIZE) // 2

        slot = pygame.Rect(
            slot_x,
            slot_y,
            INVENTORY_SLOT_SIZE,
            INVENTORY_SLOT_SIZE
        )

        # Empty inventory slot at the start.
        pygame.draw.rect(
            self.screen,
            (55, 55, 70),
            slot,
            border_radius=4
        )

        pygame.draw.rect(
            self.screen,
            (150, 150, 165),
            slot,
            2,
            border_radius=4
        )

        # Display the key immediately after pickup.
        if self.player.has_key:

            center_x = slot.centerx
            center_y = slot.centery

            # Key ring
            pygame.draw.circle(
                self.screen,
                (255, 220, 50),
                (center_x - 6, center_y - 5),
                6,
                2
            )

            # Key shaft
            pygame.draw.rect(
                self.screen,
                (255, 220, 50),
                pygame.Rect(
                    center_x - 1,
                    center_y - 2,
                    12,
                    4
                )
            )

            # Key teeth
            pygame.draw.rect(
                self.screen,
                (255, 220, 50),
                pygame.Rect(
                    center_x + 6,
                    center_y + 2,
                    3,
                    5
                )
            )

            pygame.draw.rect(
                self.screen,
                (255, 220, 50),
                pygame.Rect(
                    center_x + 2,
                    center_y + 2,
                    3,
                    4
                )
            )

    def draw(self):



        self.screen.fill(

            (30, 25, 40)

        )



        # Dungeon

        for r in range(ROWS):



            for c in range(COLS):



                cell = self.grid[r][c]



                rect = pygame.Rect(

                    c * TILE,

                    r * TILE,

                    TILE,

                    TILE

                )



                pygame.draw.rect(

                    self.screen,

                    COLORS[cell],

                    rect

                )



                # Key

                if cell == KEY:



                    pygame.draw.circle(

                        self.screen,

                        (255, 240, 60),

                        (

                            c * TILE + TILE // 2,

                            r * TILE + TILE // 2

                        ),

                        10

                    )



                # Chest

                elif cell == CHEST:



                    pygame.draw.rect(

                        self.screen,

                        (180, 120, 20),

                        rect.inflate(-12, -12),

                        border_radius=4

                    )



                # Trap

                elif cell == TRAP:



                    center_x = (

                        c * TILE + TILE // 2

                    )



                    center_y = (

                        r * TILE + TILE // 2

                    )



                    pygame.draw.circle(

                        self.screen,

                        (120, 20, 20),

                        (

                            center_x,

                            center_y

                        ),

                        13

                    )



                    points = [

                        (

                            center_x,

                            center_y - 11

                        ),

                        (

                            center_x + 5,

                            center_y + 8

                        ),

                        (

                            center_x - 5,

                            center_y + 8

                        )

                    ]



                    pygame.draw.polygon(

                        self.screen,

                        (255, 200, 40),

                        points

                    )



        # Guard

        self.guard.draw(

            self.screen

        )



        # Player

        self.player.draw(

            self.screen

        )



        # Mini-map

        self.draw_minimap()



        # HUD

        hud = pygame.Rect(

            0,

            ROWS * TILE,

            WIDTH,

            50

        )



        pygame.draw.rect(

            self.screen,

            (20, 20, 35),

            hud

        )



        status_surface = self.font.render(

            self.status + "  |  R=Restart",

            True,

            (200, 200, 200)

        )



        self.screen.blit(

            status_surface,

            (

                8,

                ROWS * TILE + 13

            )

        )



        # Task 4: inventory slot
        self.draw_inventory()

        # Win screen

        if self.won:



            overlay = pygame.Surface(

                (

                    WIDTH,

                    ROWS * TILE

                ),

                pygame.SRCALPHA

            )



            overlay.fill(

                (0, 0, 0, 140)

            )



            self.screen.blit(

                overlay,

                (0, 0)

            )



            message = self.big_font.render(

                "TREASURE FOUND!",

                True,

                (220, 180, 30)

            )



            subtitle = self.font.render(

                "Press R to Play Again",

                True,

                (180, 180, 180)

            )



            self.screen.blit(

                message,

                (

                    WIDTH // 2

                    - message.get_width() // 2,

                    ROWS * TILE // 2 - 30

                )

            )



            self.screen.blit(

                subtitle,

                (

                    WIDTH // 2

                    - subtitle.get_width() // 2,

                    ROWS * TILE // 2 + 20

                )

            )



        pygame.display.flip()



    # =========================================================

    # MAIN LOOP

    # =========================================================



    def run(self):



        running = True



        while running:



            running = self.handle_events()



            self.update()



            self.draw()



            self.clock.tick(FPS)



        pygame.quit()





# =============================================================

# START GAME

# =============================================================



if __name__ == "__main__":



    engine = GameEngine()

    engine.run()