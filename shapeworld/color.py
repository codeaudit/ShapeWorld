from random import choice, gauss
import numpy as np


class Color(object):
    __slots__ = ('name', 'rgb', 'shade', 'shaded_rgb')

    def __init__(self, name, rgb, shade):
        assert isinstance(name, str)
        assert isinstance(rgb, tuple) and len(rgb) == 3 and all(isinstance(x, float) and 0.0 <= x <= 1.0 for x in rgb)
        assert isinstance(shade, float) and -1.0 <= shade <= 1.0
        self.name = name
        self.rgb = rgb
        self.shade = shade
        if shade < 0.0:
            shaded_rgb = (rgb[0] + rgb[0] * shade, rgb[1] + rgb[1] * shade, rgb[2] + rgb[2] * shade)
        elif shade > 0.0:
            shaded_rgb = (rgb[0] + (1.0 - rgb[0]) * shade, rgb[1] + (1.0 - rgb[1]) * shade, rgb[2] + (1.0 - rgb[2]) * shade)
        else:
            shaded_rgb = rgb
        if rgb == shaded_rgb:
            self.shade = 0.0
        self.shaded_rgb = np.asarray(shaded_rgb, dtype=np.float32)

    def __str__(self):
        return self.name

    def model(self):
        return {'name': str(self), 'rgb': list(self.rgb), 'shade': self.shade}

    def __eq__(self, other):
        if isinstance(other, str):
            return str(self) == other
        return isinstance(other, Color) and str(self) == str(other)

    def get_color(self):
        return np.copy(self.shaded_rgb)  # required?

    @staticmethod
    def random_instance(colors, shade_range):
        name, rgb = choice([(color, Color.colors[color]) for color in colors])
        if shade_range > 0.0:
            shade = gauss(mu=0.0, sigma=shade_range)
            while shade < -shade_range or shade > shade_range:
                shade = gauss(mu=0.0, sigma=shade_range)
        else:
            shade = 0.0
        return Color(name, rgb, shade)


Color.colors = {
    'black': (0.0, 0.0, 0.0),
    'red': (1.0, 0.0, 0.0),
    'green': (0.0, 1.0, 0.0),
    'blue': (0.0, 0.0, 1.0),
    'yellow': (1.0, 1.0, 0.0),
    'magenta': (1.0, 0.0, 1.0),
    'cyan': (0.0, 1.0, 1.0),
    'white': (1.0, 1.0, 1.0)}
