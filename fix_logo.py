from PIL import Image

try:
    img = Image.open('LOGO.jpg')
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    # Removing white backgrounds (threshold > 220)
    for item in datas:
        if item[0] > 220 and item[1] > 220 and item[2] > 220:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    img.save("LOGO.png", "PNG")
    print("Logo successfully converted and white background removed.")
except Exception as e:
    print(f"Error: {e}")
