import pygame
import random
import numpy as np

from neuroevolution import Neuroevolution, Genome

pygame.init()

WIN_WIDTH = 500
WIN_HEIGHT = 512

GOAL = 20000

BG_COLOR = (150, 226, 130)

bird_images = [
    './assets/imgs/red_bird.png',
    './assets/imgs/blue_bird.png',
    './assets/imgs/yellow_bird.png'
]

background_images = [
    './assets/imgs/background-night.png',
    './assets/imgs/background-day.png'
]

BIRD_imgs = pygame.image.load(random.choice(bird_images))
PIPE_TOP_imgs = pygame.image.load('./assets/imgs/pipetop.png')
PIPE_BOTTOM_imgs = pygame.transform.flip(PIPE_TOP_imgs, False, True)
BACKGROUND_imgs = pygame.image.load(random.choice(background_images))

class Bird:
    def __init__(self):
        self.x = 80
        self.y = 250
        self.width = 40
        self.height = 30
        self.alive = True
        self.gravity = 0
        self.velocity = 0.3
        self.jump_strength = -6

    def flap(self):
        self.gravity = self.jump_strength

    def update(self):
        self.gravity += self.velocity
        self.y += self.gravity

    def is_dead(self, height, pipes):
        if self.y >= height or self.y + self.height <= 0:
            return True
        for pipe in pipes:
            if not (self.x > pipe.x + pipe.width or self.x + self.width < pipe.x or self.y > pipe.y + pipe.height or self.y + self.height < pipe.y):
                return True
        return False

class Pipe:
    def __init__(self, x, y, width, height, speed=3):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed

    def update(self):
        self.x -= self.speed

    def is_out(self):
        return self.x + self.width < 0

class Game:
    def __init__(self):
        self.width = WIN_WIDTH
        self.height = WIN_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Flappy Learning - PyGame')
        self.clock = pygame.time.Clock()

        self.background = BACKGROUND_imgs
        self.bird_imgs = BIRD_imgs
        self.pipe_top_imgs = PIPE_TOP_imgs
        self.pipe_bottom_imgs = PIPE_BOTTOM_imgs

        self.pipes = []
        self.birds = []
        self.score = 0
        self.max_score = 0
        self.spawn_interval = 90
        self.interval = 0

        self.neuroevolution = Neuroevolution(50, [2, 2, 1])
        self.networks = self.neuroevolution.create_initial_population()
        self.birds = [Bird() for _ in self.networks]

        self.generation = 1
        self.alives = len(self.networks)
        self.background_x = 0
        self.background_speed = 0.5

        self.max_scores_per_generation = []

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            self.update()
            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        pygame.quit()

    def update(self):
        if self.score >= GOAL:
            self.screen.fill(BG_COLOR)

            rel_x = self.background_x % self.background.get_rect().width

            self.screen.blit(self.background, (rel_x - self.background.get_rect().width, 0))
            self.screen.blit(self.background, (rel_x, 0))

            if rel_x < self.width:
                self.screen.blit(self.background, (rel_x + self.background.get_rect().width, 0))

            self.display_centered_text(self.screen, self.score, self.max_score, self.generation)

            pygame.image.save(self.screen, f'output-{GOAL}.png')

            pygame.display.flip()
            pygame.time.wait(5000)

            pygame.quit()
            quit()

        self.background_x += self.background_speed
        next_pipe = None
        for pipe in self.pipes:
            if pipe.x + pipe.width > 80:
                next_pipe = pipe
                break

        for i, bird in enumerate(self.birds):
            if bird.alive:
                inputs = [
                    bird.y / self.height,
                    (next_pipe.height / self.height) if next_pipe else 0
                ]
                output = self.networks[i].activate(inputs)
                if output[0] > 0.5:
                    bird.flap()
                bird.update()
                if bird.is_dead(self.height, self.pipes):
                    bird.alive = False
                    self.alives -= 1
                    self.neuroevolution.add_genome(Genome(self.score, self.networks[i]))
                    if self.alives == 0:
                        self.start_new_generation()
        for pipe in self.pipes:
            pipe.update()
        self.pipes = [pipe for pipe in self.pipes if not pipe.is_out()]

        self.interval += 1
        if self.interval == self.spawn_interval:
            self.interval = 0
            delta_bord = 50
            pipe_holl = 120
            holl_position = random.randint(delta_bord, self.height - delta_bord - pipe_holl)
            self.pipes.append(Pipe(self.width, 0, 40, holl_position))
            self.pipes.append(Pipe(self.width, holl_position + pipe_holl, 40, self.height - holl_position - pipe_holl))

        self.score += 1
        if self.score > self.max_score:
            self.max_score = self.score

    def display_centered_text(self, screen, score, max_score, generation):
        font = pygame.font.Font('./assets/font/flappy-font.ttf', 15)
        text_score = font.render(f'Score: {score}', True, (255, 255, 255))
        text_max_score = font.render(f'Score max: {max_score}', True, (255, 255, 255))
        text_generation = font.render(f'Generation: {generation}', True, (255, 255, 255))

        screen_rect = screen.get_rect()
        text_rect_score = text_score.get_rect(center=(screen_rect.centerx, screen_rect.centery - 20))
        text_rect_max_score = text_max_score.get_rect(center=(screen_rect.centerx, screen_rect.centery))
        text_rect_generation = text_generation.get_rect(center=(screen_rect.centerx, screen_rect.centery + 20))

        screen.blit(text_score, text_rect_score)
        screen.blit(text_max_score, text_rect_max_score)
        screen.blit(text_generation, text_rect_generation)

    def draw(self):
        self.screen.fill(BG_COLOR)
        rel_x = self.background_x % self.background.get_rect().width

        self.screen.blit(self.background, (rel_x - self.background.get_rect().width, 0))
        self.screen.blit(self.background, (rel_x, 0))
        
        # Avoir l'image de fond sur tout le fond
        if rel_x < self.width:
            self.screen.blit(self.background, (rel_x + self.background.get_rect().width, 0))

        for pipe in self.pipes:
            if pipe.y == 0:
                self.screen.blit(self.pipe_top_imgs, (pipe.x, pipe.y + pipe.height - self.pipe_top_imgs.get_height()))
            else:
                self.screen.blit(self.pipe_bottom_imgs, (pipe.x, pipe.y))

        for bird in self.birds:
            if bird.alive:
                self.screen.blit(self.bird_imgs, (bird.x, bird.y))

        font = pygame.font.Font('./assets/font/flappy-font.ttf', 15)
        text = font.render(f'Score: {self.score}', True, (255, 255, 255))
        self.screen.blit(text, (10, 10))
        text = font.render(f'Score max: {self.max_score}', True, (255, 255, 255))
        self.screen.blit(text, (10, 30))
        text = font.render(f'Generation: {self.generation}', True, (255, 255, 255))
        self.screen.blit(text, (10, 50))
        text = font.render(f'Encore en vie: {self.alives} / {self.neuroevolution.population_size}', True, (255, 255, 255))
        self.screen.blit(text, (10, 70))

        self.draw_graph()

        pygame.display.flip()

    def draw_graph(self):
        graph_width = 200
        graph_height = 100
        graph_x = self.width - graph_width - 10
        graph_y = 10

        pygame.draw.rect(self.screen, (50, 50, 50), (graph_x, graph_y, graph_width, graph_height))

        if len(self.max_scores_per_generation) > 1:
            max_score = max(self.max_scores_per_generation)

            if max_score == 0:
                max_score = 1

            scale_y = graph_height / max_score

            scale_x = graph_width / (len(self.max_scores_per_generation) - 1)

            for i in range(len(self.max_scores_per_generation) - 1):
                x1 = graph_x + i * scale_x
                y1 = graph_y + graph_height - self.max_scores_per_generation[i] * scale_y
                x2 = graph_x + (i + 1) * scale_x
                y2 = graph_y + graph_height - self.max_scores_per_generation[i + 1] * scale_y

                pygame.draw.line(self.screen, (0, 255, 0), (x1, y1), (x2, y2), 2)

        pygame.draw.rect(self.screen, (255, 255, 255), (graph_x, graph_y, graph_width, graph_height), 1)

        font = pygame.font.Font('./assets/font/flappy-font.ttf', 10)
        text = font.render('Score Max', True, (255, 255, 255))
        self.screen.blit(text, (graph_x + 5, graph_y + 5))

    def start_new_generation(self):
        self.max_scores_per_generation.append(self.max_score)
        self.score = 0
        self.pipes = []
        self.birds = []
        self.networks = self.neuroevolution.next_generation()
        for _ in self.networks:
            self.birds.append(Bird())
        self.generation += 1
        self.alives = len(self.birds)

if __name__ == '__main__':
    game = Game()
    game.run()
