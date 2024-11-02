import numpy as np
import random
import json

class SnakeHelper:
    def __init__(self, size = 32):         
        self.screen_width = size * 20
        self.screen_height = size * 20
        self.snake_size = 20
        self.snake_speed = 15
        self.snake_coords = []
        self.snake_length = 1
        self.dir = "right"
        self.board = np.zeros((self.screen_height // self.snake_size, self.screen_width // self.snake_size))
        self.game_close = False
        self.x1 = self.screen_width / 2
        self.y1 = self.screen_height / 2
        self.r1, self.c1 = self.coords_to_index(self.x1, self.y1)
        self.board[self.r1][self.c1] = 1
        self.c_change = 1
        self.r_change = 0
        self.food_r, self.food_c = self.generate_food()
        self.board[self.food_r][self.food_c] = 2
        self.survived = 0
        self.step()
    
    def get_state(self):
        head_r, head_c = self.snake_coords[-1]
        state = []
        state.append(int(self.dir == "left"))
        state.append(int(self.dir == "right"))
        state.append(int(self.dir == "up"))
        state.append(int(self.dir == "down"))
        state.append(int(self.food_r < head_r))
        state.append(int(self.food_r > head_r))
        state.append(int(self.food_c < head_c))
        state.append(int(self.food_c > head_c))
        state.append(self.is_unsafe(head_r + 1, head_c))
        state.append(self.is_unsafe(head_r - 1, head_c))
        state.append(self.is_unsafe(head_r, head_c + 1))
        state.append(self.is_unsafe(head_r, head_c - 1))
        return tuple(state)
    
    def is_unsafe(self, r, c):
        if self.valid_index(r, c):
          if self.board[r][c] == 1:
              return 1
          return 0
        else:
          return 1
        
    def get_dist(self, r1, c1, r2, c2):
        return ((r2 - r1) ** 2 + (c2 - c1) ** 2) ** 0.5
                
    def valid_index(self, r, c):
        return 0 <= r < len(self.board) and 0 <= c < len(self.board[0])
        
    def coords_to_index(self, x, y):
        r = int(y // 20)
        c = int(x // 20)
        return (r, c)
    
    def generate_food(self):
        food_c = int(round(random.randrange(0, self.screen_width - self.snake_size) / 20.0))
        food_r = int(round(random.randrange(0, self.screen_height - self.snake_size) / 20.0))
        if self.board[food_r][food_c] != 0:
            food_r, food_c = self.generate_food()
        return food_r, food_c
    
    def game_over(self):
        return self.game_close
        
    def step(self, action="None"):
        if action == "None":
            action = random.choice(["left", "right", "up", "down"])
        else:
            action = ["left", "right", "up", "down"][action]
        reward = 0
 
        if action == "left" and (self.dir != "right" or self.snake_length == 1):
            self.c_change = -1
            self.r_change = 0
            self.dir = "left"
        elif action == "right" and (self.dir != "left" or self.snake_length == 1):
            self.c_change = 1
            self.r_change = 0
            self.dir = "right"
        elif action == "up" and (self.dir != "down" or self.snake_length == 1):
            self.r_change = -1
            self.c_change = 0
            self.dir = "up"
        elif action == "down" and (self.dir != "up" or self.snake_length == 1):
            self.r_change = 1
            self.c_change = 0
            self.dir = "down"
 
        if self.c1 >= self.screen_width // self.snake_size or self.c1 < 0 or self.r1 >= self.screen_height // self.snake_size or self.r1 < 0:
            self.game_close = True
        self.c1 += self.c_change
        self.r1 += self.r_change
        
        self.snake_coords.append((self.r1, self.c1))
        
        if self.valid_index(self.r1, self.c1):
            self.board[self.r1][self.c1] = 1
        
        if len(self.snake_coords) > self.snake_length:
            rd, cd = self.snake_coords[0]
            del self.snake_coords[0]
            if self.valid_index(rd, cd):
                self.board[rd][cd] = 0
 
        for r, c in self.snake_coords[:-1]:
            if r == self.r1 and c == self.c1:
                self.game_close = True
 
        if self.c1 == self.food_c and self.r1 == self.food_r:
            self.food_r, self.food_c = self.generate_food()
            self.board[self.food_r][self.food_c] = 2
            self.snake_length += 1
            reward = 1
        else:
            rh1, ch1 = self.snake_coords[-1]
            if len(self.snake_coords) == 1:
                rh2, ch2 = rh1, ch1
            else:
                rh2, ch2 = self.snake_coords[-1]
        
        if self.game_close:
            reward = -10
        self.survived += 1
        
        return self.get_state(), reward, self.game_close
            
    def run_game(self, episode):
        filename = f"training/{episode}.json"
        with open(filename, 'rb') as file:
            table = json.load(file)
        current_length = 2
        steps_unchanged = 0
        while not self.game_over():
            state = self.get_state()
            action = np.argmax(table[state])
            if steps_unchanged == 1000:
                break
            self.step(action)
            if self.snake_length != current_length:
                steps_unchanged = 0
                current_length = self.snake_length
            else:
                steps_unchanged += 1
                
        return self.snake_length
            
class TrainSnake():
    def __init__(self):
        self.discount_rate = 0.95
        self.learning_rate = 0.01
        self.eps = 1.0
        self.eps_discount = 0.9992
        self.min_eps = 0.001
        self.num_episodes = 20000
        self.table = np.zeros((2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4))
        self.env = SnakeHelper()
        self.score = []
        self.survived = []
        
    def get_action(self, state):
        if random.random() < self.eps:
            return random.choice([0, 1, 2, 3])
        
        return np.argmax(self.table[state])
    
    def train(self, size = 32):
        for i in range(1, self.num_episodes + 1):
            self.env  = SnakeHelper(size)
            steps_without_food = 0
            length = self.env.snake_length
            
            if i % 25 == 0:
                print(f"Episodes: {i}, score: {np.mean(self.score)}, survived: {np.mean(self.survived)}, eps: {self.eps}, lr: {self.learning_rate}")
                self.score = []
                self.survived = []
               
            if (i < 500 and i % 10 == 0) or (i >= 500 and i < 1000 and i % 200 == 0) or (i >= 1000 and i % 500 == 0):
                with open(f'training/{i}.json', 'w') as file:
                    json.dump(self.table.tolist(), file)

                
            current_state = self.env.get_state()
            self.eps = max(self.eps * self.eps_discount, self.min_eps)
            done = False
            while not done:
                action = self.get_action(current_state)
                new_state, reward, done = self.env.step(action)
                
                self.table[current_state][action] = (1 - self.learning_rate)\
                    * self.table[current_state][action] + self.learning_rate\
                    * (reward + self.discount_rate * max(self.table[new_state])) 
                current_state = new_state
                
                steps_without_food += 1
                if length != self.env.snake_length:
                    length = self.env.snake_length
                    steps_without_food = 0
                if steps_without_food == 1000:
                    break
            
            self.score.append(self.env.snake_length - 1)
            self.survived.append(self.env.survived)

class RandomPlayer():
    def __init__(self, game):
        self.game = game

    def run(self, training_number):
        self.game.run_game(-1)

    def train(self):
        raise NotImplementedError

class AiPlayer():
    def __init__(self, game):
        self.game = game
        self.trainer = TrainSnake()

    def run(self, training_number):
        self.game.run_game(training_number)

    def train(self):
        self.trainer.train(int(self.game.game_width / 20))