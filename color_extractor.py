from colorthief import ColorThief

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def get_colors(image_path):
    color_thief = ColorThief(image_path)
    dominant = color_thief.get_color(quality=1)
    palette = color_thief.get_palette(color_count=5)
    return {
        "dominant_hex": rgb_to_hex(dominant),
        "palette_hex": [rgb_to_hex(c) for c in palette],
    }

if __name__ == "__main__":
    colors = get_colors("test.jpg")
    print(colors)