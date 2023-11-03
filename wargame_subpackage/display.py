import pygame
import re

class DisplayItem:
    def __init__(self, text, x, y, width, height, color, top = False):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.width = width
        self.height = height
        self.position = self.get_position()
        self.top = top
    
    def get_position(self):
        return (self.x, self.y, self.width, self.height)

    def get_text_position(self, text):
        if self.top:
            return (self.x, self.y)
        return (self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/4) - round(text.get_height()/2))

    def get_text_position_multiline(self, text, line_number):
        if self.top:
            return (self.x, self.y + (line_number * round(text.get_height() + 5)))
        return (self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/4) - round(text.get_height()/2) + (line_number * round(text.get_height() + 5)))

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.position)
        font = pygame.font.SysFont("arial", 20)
        if re.search(r'\n', self.text): # Multi-line string hack
            line_number = 0
            for line in self.text.split("\n"):
                text = font.render(line, 1, (0, 0, 0))
                win.blit(text, self.get_text_position_multiline(text, line_number))
                line_number += 1
        else:
            text = font.render(self.text, 1, (0, 0, 0))
            win.blit(text, self.get_text_position(text))
                    


class UpdatedDisplayItem(DisplayItem):
    def __init__(self, text,  x, y, width, height, color, pos = False):
        DisplayItem.__init__(self, text, x, y, width, height, color, pos)

    def update_text(self, new_text):
        self.text = new_text

class ClickableDisplayItem(DisplayItem):
    def __init__(self, text, x, y, width, height, color, card):
        DisplayItem.__init__(self, text, x, y, width, height, color)
        self.card = card
        self.clicked = False

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False

    def was_clicked(self):
        self.clicked = True
