"""
System symulacji sterowania samochodem oparty na logice rozmytej. System ma na celu sterowanie pojazdem, który porusza
się w ograniczonym obszarze, i umożliwia mu unikanie kolizji z bocznymi ścianami. Samochód zbiera informacje o odległości
od ścian na podstawie trzech promieni (lewy, centralny, prawy) i decyduje o skręcie oraz przyspieszeniu, aby płynnie nawigować
w przestrzeni.

Autor rozwiązania:
- Karol Szmajda

Wejścia systemu:
1. `left_distance`: Odległość od ściany z lewej strony.
2. `center_distance`: Odległość od ściany na wprost.
3. `right_distance`: Odległość od ściany z prawej strony.

Wyjścia systemu:
1. `turn_value`: Wartość sterująca kierunkiem (w lewo lub w prawo).
2. `acceleration_value`: Wartość przyspieszenia samochodu, opisana za pomocą trzech funkcji przynależności:
- `near` - przyspieszenie w przypadku bliskości ściany,
- `medium` - umiarkowane przyspieszenie przy średniej odległości,
- `far` - przyspieszenie przy dużej odległości od ściany.
"""


import pygame
import math
from fuzzylogic.classes import Domain
from fuzzylogic.functions import S, R

# Parametry okna gry
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BG_COLOR = (30, 30, 30)
WALL_COLOR = (200, 200, 200)
CAR_COLOR = (0, 150, 255)
TEXT_COLOR = (255, 255, 255)
RAY_COLOR = (255, 0, 0)

# Ustawienia samochodu
CAR_SIZE = (20, 40)
CAR_SPEED = 2

# Definicje domen rozmytych dla odległości
distance_domain = Domain("Distance", 0, 100)
distance_domain.near = S(0, 50)     # Blisko
distance_domain.medium = S(40, 180)  # Średnia odległość
distance_domain.far = R(100, 200)    # Daleko

def calculate_control(left_distance, center_distance, right_distance):
 """
 Funkcja logiki rozmytej do sterowania samochodem.
 
 Args:
     left_distance (float): Odległość od lewej ściany.
     center_distance (float): Odległość od ściany na wprost.
     right_distance (float): Odległość od prawej ściany.
 
 Returns:
     tuple: Zawiera wartości sterujące samochodem:
         - turn_value (float): Wartość skrętu samochodu (w lewo lub w prawo).
         - acceleration_value (float): Wartość przyspieszenia samochodu.
         - Przynależności dla każdej odległości (near, medium, far) dla celów debugowania.
 """
 f_left_near = distance_domain.near(left_distance)
 f_left_medium = distance_domain.medium(left_distance)
 f_left_far = distance_domain.far(left_distance)

 f_center_near = distance_domain.near(center_distance)
 f_center_medium = distance_domain.medium(center_distance)
 f_center_far = distance_domain.far(center_distance)

 f_right_near = distance_domain.near(right_distance)
 f_right_medium = distance_domain.medium(right_distance)
 f_right_far = distance_domain.far(right_distance)

 # Wyznaczanie wartości skrętu
 turn_left = f_right_near * -1.0 + f_right_medium * 0.5 + (1 - f_center_far) * 0.8
 turn_right = f_left_near * 1.0 + f_left_medium * 0.5 + (1 - f_left_far) * -0.6
 turn_value = turn_left + turn_right

 # Wyznaczanie wartości przyspieszenia
 slow_down = f_center_near * -1
 moderate_speed = f_center_medium * 0.8
 speed_up = f_center_far * 1
 acceleration_value = (slow_down + moderate_speed + speed_up)

 # Przycięcie wyników do zakresu <-1, 1>
 turn_value = max(-1, min(1, turn_value))
 acceleration_value = max(-1, min(1, acceleration_value))

 return (turn_value, acceleration_value, 
         f_left_near, f_left_medium, f_left_far,
         f_center_near, f_center_medium, f_center_far,
         f_right_near, f_right_medium, f_right_far)

def draw_text(screen, text, position):
 """
 Funkcja pomocnicza do rysowania tekstu na ekranie.

 Args:
     screen (pygame.Surface): Powierzchnia, na której rysowany jest tekst.
     text (str): Treść tekstu do wyświetlenia.
     position (tuple): Pozycja na ekranie, w której tekst ma być wyświetlony.
 """
 font = pygame.font.Font(None, 30)
 text_surface = font.render(text, True, TEXT_COLOR)
 screen.blit(text_surface, position)

def get_distance_to_wall(pos, angle, walls):
 """
 Funkcja obliczająca odległość od ściany w danym kierunku (kącie).

 Args:
     pos (tuple): Pozycja samochodu (x, y).
     angle (float): Kąt, w którym promień jest wysyłany.
     walls (set): Zbiór punktów reprezentujących ściany.
 
 Returns:
     int: Odległość do ściany w danym kierunku.
 """
 for dist in range(1, 200):
     x = pos[0] + dist * math.cos(math.radians(angle))
     y = pos[1] + dist * math.sin(math.radians(angle))
     if (int(x), int(y)) in walls:
         return dist
 return 200

def main():
 """
 Główna funkcja gry inicjalizująca pygame, wczytująca logikę fuzzy i obsługująca rysowanie samochodu
 oraz jego promieni. Zajmuje się również reagowaniem samochodu na przeszkody.
 """
 pygame.init()
 screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
 clock = pygame.time.Clock()

 # Inicjalizacja samochodu
 car_pos = [400, 300]
 car_angle = 0

 # Utwórz powierzchnię samochodu
 car_surface = pygame.Surface(CAR_SIZE, pygame.SRCALPHA)
 car_surface.fill(CAR_COLOR)

 walls = set()
 for x in range(0, SCREEN_WIDTH):
     walls.add((x, 0))
     walls.add((x, SCREEN_HEIGHT - 1))
 for y in range(0, SCREEN_HEIGHT):
     walls.add((0, y))
     walls.add((SCREEN_WIDTH - 1, y))

 running = True
 while running:
     for event in pygame.event.get():
         if event.type == pygame.QUIT:
             running = False

     left_dist = get_distance_to_wall(car_pos, car_angle - 45, walls)
     center_dist = get_distance_to_wall(car_pos, car_angle, walls)
     right_dist = get_distance_to_wall(car_pos, car_angle + 45, walls)

     (turn, acceleration,
      f_left_near, f_left_medium, f_left_far,
      f_center_near, f_center_medium, f_center_far,
      f_right_near, f_right_medium, f_right_far) = calculate_control(left_dist, center_dist, right_dist)

     car_angle += turn * 2
     speed = CAR_SPEED * acceleration
     car_pos[0] += speed * math.cos(math.radians(car_angle))
     car_pos[1] += speed * math.sin(math.radians(car_angle))

     screen.fill(BG_COLOR)
     for wall in walls:
         screen.set_at(wall, WALL_COLOR)

     rotated_car = pygame.transform.rotate(car_surface, -car_angle)
     car_rect = rotated_car.get_rect(center=car_pos)
     screen.blit(rotated_car, car_rect.topleft)

     angles = [car_angle - 45, car_angle, car_angle + 45]
     distances = [left_dist, center_dist, right_dist]
     for angle, dist in zip(angles, distances):
         end_x = car_pos[0] + dist * math.cos(math.radians(angle))
         end_y = car_pos[1] + dist * math.sin(math.radians(angle))
         pygame.draw.line(screen, RAY_COLOR, car_pos, (end_x, end_y), 1)

     draw_text(screen, f"Left Distance: {left_dist:.2f}", (10, 10))
     draw_text(screen, f"Left Near: {f_left_near:.2f}, Medium: {f_left_medium:.2f}, Far: {f_left_far:.2f}", (10, 40))
     draw_text(screen, f"Center Distance: {center_dist:.2f}", (10, 70))
     draw_text(screen, f"Center Near: {f_center_near:.2f}, Medium: {f_center_medium:.2f}, Far: {f_center_far:.2f}", (10, 100))
     draw_text(screen, f"Right Distance: {right_dist:.2f}", (10, 130))
     draw_text(screen, f"Right Near: {f_right_near:.2f}, Medium: {f_right_medium:.2f}, Far: {f_right_far:.2f}", (10, 160))
     draw_text(screen, f"Turn: {turn:.2f}", (10, 190))
     draw_text(screen, f"Acceleration: {acceleration:.2f}", (10, 220))

     pygame.display.flip()
     clock.tick(144)

 pygame.quit()

if __name__ == "__main__":
 main()