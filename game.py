import random
from tile import *
from entity import *


class Game:
    def __init__(self, map_size):
        self.size = map_size
        self.tiles = self.gen_tiles(map_size)
        self.exit = False
        self.current_display = [0, 0]
        self.time_passed = 0
        self.paused = True
        self.entities = []

    def gen_tiles(self, map_size):
        game_map = []
        for i in range(map_size):
            map_column = []
            for j in range(map_size):
                map_column.append(Tile())
            game_map.append(map_column)
        return game_map

    def make_tiles(self, foods):
        array = []
        for column in foods:
            sub_array = []
            for food in column:
                tile = Tile(food)
                sub_array.append(tile)
            array.append(sub_array)
        return array

    def max_food(self):
        max_food = 1
        for column in self.tiles:
            for tile in column:
                if tile.food > max_food:
                    max_food = tile.food
        return max_food

    def tick(self):
        if not self.paused:
            self.time_passed += 1
            self.add_food()
            self.physics()
            if random.randint(0, 100) == 1:
                self.gen_entity()

    def physics(self):
        self.move_bodies()
        self.check_wall_collisions()

    def check_wall_collisions(self):
        for entity in self.entities:
            for body in entity.bodies:
                if body.location[0] > self.size:
                    body.location[0] = self.size * 2 - body.location[0]
                    body.velocity[0] = -body.velocity[0]
                if body.location[1] > self.size:
                    body.location[1] = self.size * 2 - body.location[1]
                    body.velocity[1] = -body.velocity[1]
                if body.location[0] < 0:
                    body.location[0] = -body.location[0]
                    body.velocity[0] = -body.velocity[0]
                if body.location[1] < 0:
                    body.location[1] = -body.location[1]
                    body.velocity[1] = -body.velocity[1]

    def move_bodies(self):
        for entity in self.entities:
            for body in entity.bodies:
                body.location[0] += body.velocity[0]
                body.location[1] += body.velocity[1]

    def gen_entity(self):
        rand_x = random.randint(0, self.size - 1)
        rand_y = random.randint(0, self.size - 1)
        rand_x_vel = random.random() * 2 - 1
        rand_y_vel = random.random() * 2 - 1
        entity = Entity()
        entity.bodies.append(Body())
        entity.bodies[0].location = [rand_x + 0.5, rand_y + 0.5]
        entity.bodies[0].size = 0.4
        entity.bodies[0].mouth_size = 0.1
        entity.bodies[0].velocity = [rand_x_vel, rand_y_vel]
        self.entities.append(entity)

    def add_food(self):
        for i in range(self.size):
            for j in range(self.size):
                self.tiles[i][j].food += random.random()

    def save(self):
        file = open("data.data", "wb")
        time_array = self.number_to_bytes(self.time_passed, 3, 0)
        size_array = self.number_to_bytes(self.size, 2, 0)
        food_array = self.food_to_bytes()
        entity_array = self.entities_to_bytes()

        array = self.add_arrays([time_array, size_array, food_array, entity_array])

        b_array = bytearray(array)
        file.write(b_array)
        file.close()

    def load(self):
        file = open("data.data", "rb")
        data = bytearray(file.read())
        file.close()

        data = self.load_time(data)

        data = self.load_size(data)

        data = self.load_food(data)

        data = self.load_entities(data)

    def load_entities(self, data):
        self.entities = []

        entity_amount = int(self.bytes_to_number(data[:2], 2, 0))
        del data[:2]

        for i in range(entity_amount):
            data = self.load_entity(data)
        return data

    def load_entity(self, data):
        entity = Entity()
        body_amount = int(self.bytes_to_number(data[:1], 1, 0))
        del data[:1]

        for j in range(body_amount):
            data, entity = self.load_body(data, entity)
        self.entities.append(entity)
        return data

    def load_body(self, data, entity):
        body = Body()

        x_loc = self.bytes_to_number(data[:3], 1, 2)
        del data[:3]
        y_loc = self.bytes_to_number(data[:3], 1, 2)
        del data[:3]
        size = self.bytes_to_number(data[:3], 1, 2)
        del data[:3]
        mouth_size = self.bytes_to_number(data[:3], 1, 2)
        del data[:3]
        x_vel = self.bytes_to_number(data[:3], 1, 2)
        del data[:3]
        y_vel = self.bytes_to_number(data[:3], 1, 2)
        del data[:3]

        body.location = [x_loc, y_loc]
        body.size = size
        body.mouth_size = mouth_size
        body.velocity = [x_vel, y_vel]
        entity.bodies.append(body)
        return data, entity

    def load_food(self, data):
        food_bytes = data[:self.size * self.size * 3]
        del data[:self.size * self.size * 3]
        food = self.bytes_to_food(food_bytes)
        self.tiles = self.make_tiles(food)
        return data

    def load_size(self, data):
        size_bytes = data[:2]
        del data[:2]
        self.size = int(self.bytes_to_number(size_bytes, 2, 0))
        return data

    def load_time(self, data):
        time_bytes = data[:3]
        del data[:3]
        self.time_passed = int(self.bytes_to_number(time_bytes, 3, 0))
        return data

    def entities_to_bytes(self):
        entity_bytes = self.number_to_bytes(len(self.entities), 2, 0)
        for entity in self.entities:
            entity_bytes = self.add_arrays([entity_bytes, self.entity_to_bytes(entity)])
        return entity_bytes

    def entity_to_bytes(self, entity):
        body_bytes = self.number_to_bytes(len(entity.bodies), 1, 0)
        for body in entity.bodies:
            body_bytes = self.add_arrays([body_bytes, self.body_to_bytes(body)])
        return body_bytes

    def body_to_bytes(self, body):
        x_bytes = self.number_to_bytes(body.location[0], 1, 2)
        y_bytes = self.number_to_bytes(body.location[1], 1, 2)
        size_bytes = self.number_to_bytes(body.size, 1, 2)
        mouth_size_bytes = self.number_to_bytes(body.mouth_size, 1, 2)
        x_vel_bytes = self.number_to_bytes(body.velocity[0], 1, 2)
        y_vel_bytes = self.number_to_bytes(body.velocity[1], 1, 2)
        body_bytes = self.add_arrays([x_bytes, y_bytes, size_bytes, mouth_size_bytes, x_vel_bytes, y_vel_bytes])
        return body_bytes

    def bytes_to_food(self, array):
        food_array = []
        for i in range(self.size):
            food_column = []
            for j in range(self.size):
                food = self.bytes_to_number(array[(i*self.size + j) * 3:(i*self.size + j + 1) * 3], 2, 1)
                food_column.append(food)
            food_array.append(food_column)
        return food_array

    def add_arrays(self, arrays):
        array = []
        for arr in arrays:
            for item in arr:
                array.append(item)
        return array

    def food_to_bytes(self):
        array = []
        for i in range(self.size):
            for j in range(self.size):
                food = int(self.tiles[i][j].food)
                food_array = self.number_to_bytes(food, 2, 1)
                for food in food_array:
                    array.append(food)
        return array

    def number_to_bytes(self, number, max_size, precision):
        array = []
        number += 256**max_size / 2
        number *= 256**precision
        number = int(number)
        total = max_size + precision
        for i in range(total):
            array.append((number % 256**(total - i)) // 256**(total - i - 1))
        return array

    def bytes_to_number(self, array, max_size, precision):
        value = 0
        total = max_size + precision
        for i in range(total):
            value += array[i] * 256**(total - i - 1)
        value /= 256**precision
        value -= 256**max_size / 2
        return value
