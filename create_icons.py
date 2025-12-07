from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size):
    # Create image with gradient background
    img = Image.new('RGBA', (size, size), (59, 130, 246, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw rounded rectangle background
    draw.rounded_rectangle([(0, 0), (size, size)], radius=size//6, fill=(30, 64, 175, 255))
    
    # Calculate sizes
    center = size // 2
    dollar_width = size // 8
    dollar_height = size // 2
    
    # Draw dollar sign (simplified)
    # Vertical line
    draw.rectangle(
        [center - dollar_width//2, center - dollar_height, 
         center + dollar_width//2, center + dollar_height],
        fill=(255, 255, 255, 255)
    )
    
    # Top S curve (simplified as rectangle)
    draw.ellipse(
        [center - dollar_height//2, center - dollar_height, 
         center + dollar_height//2, center - dollar_height//3],
        fill=(255, 255, 255, 255)
    )
    
    # Bottom S curve (simplified as rectangle)
    draw.ellipse(
        [center - dollar_height//2, center + dollar_height//3, 
         center + dollar_height//2, center + dollar_height],
        fill=(255, 255, 255, 255)
    )
    
    # Add decorative circles
    circle_r = size // 30
    positions = [(size//6, size//6), (size*5//6, size//6), 
                 (size//6, size*5//6), (size*5//6, size*5//6)]
    for pos in positions:
        draw.ellipse([pos[0]-circle_r, pos[1]-circle_r, 
                     pos[0]+circle_r, pos[1]+circle_r], 
                     fill=(255, 255, 255, 80))
    
    return img

# Create icons
os.makedirs('static/img', exist_ok=True)

print("Creating 512x512 icon...")
icon_512 = create_icon(512)
icon_512.save('static/img/icon-512.png', 'PNG')

print("Creating 192x192 icon...")
icon_192 = create_icon(192)
icon_192.save('static/img/icon-192.png', 'PNG')

print("✅ Icons created successfully!")
print("   - static/img/icon-512.png")
print("   - static/img/icon-192.png")
