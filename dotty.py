import pygame
import sys
import nlp_module
import time
import random

# Initialize Pygame
pygame.init()

# Set up screen
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption('Pygame Text Input Example')

# Define colors
DEFAULT = (225, 225, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 225, 0)
GREEN = (0, 225, 0)
BLACK = (0, 0, 0)

# Set up font
font = pygame.font.Font(None, 36)

# Object properties
rect_x, rect_y = 300, 300
rect_width, rect_height = 30, 30
rect_color = BLUE
speed = 70
height = 50


#Blink variables
blink_active = False
blink_start_time = None
blink_interval = 0.5  # Toggle every 0.5 seconds
blink_color = BLACK  # Blinking color
default_color = BLUE  # Default color

# Jump variables
is_jumping = False
jump_start_time = None
jump_duration = 0.5  # Half a second jump duration
jump_start_x = None
jump_start_y = None
jump_direction = None  # Can be 'left', 'right', or None (for vertical jump)
jump_height = 50
jump_distance = 70

# Input text field
input_text = ''
command_executed = False
reaction = ''

previous_positions = []

# Function to store the current position
def store_previous_position():
    global previous_positions
    previous_positions.append((rect_x, rect_y))  # Store the current position (x, y)
    if len(previous_positions) > 1:
        previous_positions = previous_positions[-1:]  # Keep only one previous position (for this example)

# Function to handle commands
def handle_command(command):
    global rect_x, rect_y, rect_color, command_executed, is_jumping, jump_start_time, jump_direction, jump_start_x, jump_start_y, blink_active, blink_start_time

    command_executed = False  # Reset state
    
    # Store the position before any movement
    if command in ['move_left', 'move_right', 'jump_left', 'jump_right', 'jump']:
        store_previous_position()
        
    # Simple commands to move or change color
    if command == 'move_left':
        rect_x -= speed
        command_executed = True
    elif command == 'move_right':
        rect_x += speed
        command_executed = True
    elif command == 'move_up' or command == 'jump_up':
        rect_y -= speed
        command_executed = True
    elif command == 'move_down':
        rect_y += speed
        command_executed = True
    elif command == 'move':
        blink_active = True
        blink_start_time = time.time()
        command_executed = True
    elif command == 'color':
        rect_color = (random.randint(10, 225), random.randint(10, 200), random.randint(10, 225))
        command_executed = True
    elif command == 'red':
        rect_color = RED
        command_executed = True
    elif command == 'blue':
        rect_color = BLUE
        command_executed = True
    elif command == 'green':
        rect_color = GREEN
        command_executed = True
    elif command == 'yellow':
        rect_color = YELLOW
        command_executed = True
    elif command == 'move_back' or command == 'jump_back':  # Go back to the previous position
        if previous_positions:
            rect_x, rect_y = previous_positions.pop()  # Restore the last stored position
        command_executed = True

    elif command == 'jump_left':
        if not is_jumping:  # Only start the jump if not already jumping
            is_jumping = True
            jump_start_time = time.time()  # Set the start time of the jump
            jump_direction = 'left'
            jump_start_x = rect_x
            jump_start_y = rect_y
        command_executed = True

    elif command == 'jump_right':
        if not is_jumping:  # Only start the jump if not already jumping
            is_jumping = True
            jump_start_time = time.time()  # Set the start time of the jump
            jump_direction = 'right'
            jump_start_x = rect_x
            jump_start_y = rect_y
        command_executed = True
        
    elif command == 'jump':
        if not is_jumping:  # Only start a new jump if not already jumping
            is_jumping = True
            jump_start_time = time.time()  # Start time of the jump
            jump_direction = None  # Simple vertical jump, no direction
            jump_start_x = rect_x
            jump_start_y = rect_y
        command_executed = True

    elif command == 'idk':
        command_executed = True
        
    elif command == 'reset':
        rect_x = 100  # Reset position
        rect_color = BLUE  # Reset color
        command_executed = True

# Main loop
running = True
while running:
    screen.fill(WHITE)
    
    # Handle blinking
    if blink_active:
        current_time = time.time()
        elapsed_time = current_time - blink_start_time
        
        # Toggle between default and blink color based on the elapsed time
        if int(elapsed_time // blink_interval) % 2 == 0:
            rect_color = blink_color
        else:
            #Finish blinking
            rect_color = default_color
            blink_active = False

    # Handle jumping (non-blocking)
    if is_jumping and jump_start_y is not None:
        current_time = time.time()
        elapsed_time = current_time - jump_start_time
        
        if elapsed_time <= jump_duration:  # Jumping up
            rect_y = jump_start_y - (jump_height * (elapsed_time / jump_duration))
            
            # Jumping left or right based on direction
            if jump_direction == 'left':
                rect_x = jump_start_x - (jump_distance * (elapsed_time / jump_duration))
            elif jump_direction == 'right':
                rect_x = jump_start_x + (jump_distance * (elapsed_time / jump_duration))
            

        elif elapsed_time <= jump_duration * 2:  # Falling back down
            rect_y = jump_start_y - jump_height + (jump_height * ((elapsed_time - jump_duration) / jump_duration))
                
        else:
            # End the jump
            is_jumping = False  # Jump is done

    # Draw the rectangle (object)
    #pygame.draw.circle(screen, rect_color, (rect_x, rect_y, rect_width, rect_height))
    #Circle
    pygame.draw.circle(screen, rect_color, (rect_x, rect_y), 20)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Capture keyboard input
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # On Enter, execute the command
                action, reaction = nlp_module.process_input('Please to ' + input_text.lower())
                if action == 'idk':
                    reaction = "Oops, i can't do it"
                handle_command(action)  # Convert input to lowercase
                input_text = ''  # Clear input after execution
            elif event.key == pygame.K_BACKSPACE:  # Handle backspace
                input_text = input_text[:-1]
            else:
                input_text += event.unicode  # Append typed character to input

    # Render input text
    font = pygame.font.Font(None, 30)
    input_surface = font.render("ASK ME: " + input_text, True, (0, 0, 0))
    screen.blit(input_surface, (20, 340))

    # Display feedback after command execution
    if command_executed:
        feedback_surface = font.render("Dotty: "+reaction, True, (0, 150, 0))
        screen.blit(feedback_surface, (20, 370))

    # Update display
    pygame.display.flip()

    # Limit frame rate
    pygame.time.Clock().tick(30)

# Quit Pygame
pygame.quit()
sys.exit()

