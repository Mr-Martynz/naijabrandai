from colorthief import ColorThief

# Point to our test image
color_thief = ColorThief("test.jpg")

# Get the single most dominant color
dominant_color = color_thief.get_color(quality=1)

# Get a palette of the top few colors
palette = color_thief.get_palette(color_count=5)

print("Dominant color (RGB):", dominant_color)
print("Full palette (RGB):", palette)

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

print("Dominant color (HEX):", rgb_to_hex(dominant_color))
print("Palette (HEX):", [rgb_to_hex(c) for c in palette])