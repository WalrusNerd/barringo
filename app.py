from flask import Flask, render_template, request, redirect, url_for, session
import random
import os
from PIL import ImageFont, ImageDraw, Image

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "barringo-secret"  # Replace with your own secure key

ITEMS_FILE = "bingo_items.txt"
ADMIN_PASSWORD = "password123"

def load_items():
    if os.path.exists(ITEMS_FILE):
        with open(ITEMS_FILE, "r") as file:
            return [line.strip() for line in file.readlines()]
    return []

def save_items(items):
    with open(ITEMS_FILE, "w") as file:
        file.write("\n".join(items))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password")
        if not session.get("authenticated"):
            if password == ADMIN_PASSWORD:
                session["authenticated"] = True
            else:
                return "Invalid password.", 403

        new_items = request.form.get("items", "").split(",")
        new_items = [item.strip() for item in new_items if item.strip()]
        items = load_items() + new_items
        save_items(list(set(items)))

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
    session.pop("authenticated", None)
    return redirect(url_for("index"))

@app.route("/play", methods=["GET", "POST"])
def play():
    items = load_items()
    if len(items) < 25:
        return "Not enough items to generate a Bingo board! Add more in admin mode."

    board_items = random.sample(items, 25)

    def calculate_font_size(text, box_width, box_height):
        font_size = 19
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

        margin = 4
        box_width -= margin
        box_height -= margin

        while font_size > 14:
            temp_image = Image.new("RGB", (box_width, box_height))
            draw = ImageDraw.Draw(temp_image)

            words = text.split()
            lines = []
            current_line = ""

            # Word wrapping logic for fitting text within the box
            for word in words:
                test_line = f"{current_line} {word}".strip()
                text_bbox = draw.textbbox((0, 0), test_line, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                if text_width <= box_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)

            wrapped_text = "\n".join(lines)

            # Measure the text's bounding box
            text_bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            # Ensure both width and height fit within the box
            if text_width <= box_width and text_height <= box_height:
                return font_size

            font_size -= 1
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()

        return font_size


    cell_size = 120
    board = []
    for i in range(5):
        row = []
        for j in range(5):
            text = board_items[i * 5 + j]
            font_size = calculate_font_size(text, cell_size, cell_size)
            row.append({"text": text, "font_size": font_size})
        board.append(row)

    return render_template("play.html", board=board)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
