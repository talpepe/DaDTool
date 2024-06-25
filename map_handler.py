import json
from json import JSONDecodeError


class Map:
    def __init__(self, image_path, title):
        self.image_path = image_path
        self.title = title

    def get_image_path(self):
        return self.image_path

    def get_image_title(self):
        return self.title

        img1 = cv2.imread("C:\\Users\\Tal P\\PycharmProjects\\DaDTool\\maps\\test.png", cv2.IMREAD_GRAYSCALE)  # queryImage
        img2 = cv2.imread("C:\\Users\\Tal P\\PycharmProjects\\DaDTool\\maps\\2.png", cv2.IMREAD_GRAYSCALE)  # trainImage

class MapHandler:
    def __init__(self):
        self.maps = []
        self.json_file_name = 'maps.json'
    def add_map(self, image_path, title):
        new_map = Map(image_path, title)
        self.maps.append(new_map)

    def clear_maps(self):
        self.maps = []
        self.save_maps()

    def save_maps(self):
        with open(self.json_file_name, 'w') as file:
            json_templates = [{'image_path': t.image_path, 'title': t.title} for t in self.maps]
            json.dump(json_templates, file)

    def load_maps(self):
        try:
            with open(self.json_file_name, 'r') as file:
                try:
                    json_maps = json.load(file)
                    self.maps = [Map(t['image_path'], t['title']) for t in json_maps]
                except JSONDecodeError:
                    self.maps = []
        except FileNotFoundError:
            self.maps = []

    def get_maps(self):
        self.load_maps()
        return self.maps

    def get_maps_as_lb_string(self):
        map_string = ""
        for map in self.maps:
            map_string += map.title + "\n"

        return map_string

