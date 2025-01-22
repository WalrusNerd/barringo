from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random
import os
from PIL import ImageFont, ImageDraw, Image

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "barringo-secret"  # Replace with your own secure key

# Paths for resources
ITEMS_FILE = "bingo_items.txt"  # File to store Bingo terms

# Admin credentials (feel free to change this)
ADMIN_PASSWORD = "password123"

# Load Bingo terms from file
def load_items():
    """Load Bingo items from the text file."""
    if os.path.exists(ITEMS_FILE):
        with open(ITEMS_FILE, "r") as file:
            return [line.strip() for line in file.readlines()]
    return []

# Save Bingo terms to file
def save_items(items):
    """Save Bingo items to the text file."""
    with open(ITEMS_FILE, "w") as file:
        file.write("\n".join(items))

@app.route("/")
def index():
    """Homepage with title and buttons."""
    return render_template("index.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Admin page for managing Bingo items."""
    if request.method == "POST":
        if not session.get("authenticated"):
            # Authenticate admin
            password = request.form.get("password")
            if password == ADMIN_PASSWORD:
                session["authenticated"] = True
            else:
                return "Invalid password.", 403

        # Add new items
        new_items = request.form.get("items", "").split(",")
        new_items = [item.strip() for item in new_items if item.strip()]
        items = load_items() + new_items
        save_items(list(set(items)))  # Avoid duplicates

    # Remove item if requested
    item_to_remove = request.args.get("remove")
    if item_to_remove:
        items = load_items()
        if item_to_remove in items:
            items.remove(item_to_remove)
            save_items(items)

    items = load_items()
    return render_template("admin.html", items=items)

@app.route("/logout")
def logout():
    """Logout admin."""
    session.pop("authenticated", None)
    return redirect(url_for("index"))

@app.route("/play", methods=["GET", "POST"])
def play():
    """Generate and display the Bingo board."""
    items = load_items()
    if len(items) < 25:
        return "Not enough items to generate a Bingo board! Add more in admin mode."

    # Randomly select 25 items for the board
    board_items = random.sample(items, 25)

    # Define font size adjustment logic
    def calculate_font_size(text, max_width, max_height):
        base_font_size = 30  # Starting font size
        temp_img = Image.new("RGB", (1, 1))  # Dummy image for text measurement
        draw = ImageDraw.Draw(temp_img)
        while base_font_size > 10:  # Minimum font size
            test_font = ImageFont.truetype("arial.ttf", base_font_size)
            text_bbox = draw.textbbox((0, 0), text, font=test_font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            if text_width <= max_width and text_height <= max_height:
                break
            base_font_size -= 2
        return base_font_size

    # Create the Bingo board with dynamic font sizes
    cell_size = 150  # Fixed cell size (uniform grid)
    board = []
    for i in range(5):
        row = []
        for j in range(5):
            text = board_items[i * 5 + j]
            font_size = calculate_font_size(text, cell_size - 10, cell_size - 10)  # Adjust for padding
            row.append({"text": text, "font_size": font_size})
        board.append(row)

    # Render the Bingo board
    return render_template("play.html", board=board)

def main():
    """Main function to run the app."""
    print("Starting the BARRINGO app...")
    app.run(debug=True)

if __name__ == "__main__":
    main()
