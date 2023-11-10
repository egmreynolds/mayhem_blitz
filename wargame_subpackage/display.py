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
        
# From stackoverflow:        
class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (0,0,0)
        self.text = text
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = True
            else:
                self.active = False
            
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                    
    def draw(self, win):
        font = pygame.font.SysFont("arial", 20)
        text = font.render(self.text, 1, (0, 0, 0))
        # Blit the text.
        win.blit(text, (self.x, self.y))
        # Blit the rect.
        pygame.draw.rect(win, self.color, self.rect, 2)

