from PIL import Image
import numpy as np
import subprocess
import asyncio
import time
import cv2
import os

first_img = input("first name: ") # input should be like: ./IMG_NAME.IMG_FORMAT (for example: ./harry_potter.png)
second_img = input("second image name: ") # input should be a diffrent image from the first like: ./IMG_NAME.IMG_FORMAT (for example: ./shrek.jpeg)

start = time.time()

def resize_image(img_path1, img_path2):
    img1 = Image.open(img_path1)
    img2 = Image.open(img_path2)

    img1.convert("RGB")

    img = img1.resize((img2.size[0], img2.size[1]), Image.Resampling.LANCZOS)
    img.save('./temp/somepic.jpg')

resize_image(first_img, second_img)

def update_pixel(r, g, b, r2, g2, b2, change_ratio):
    r2 += change_ratio if r > r2 and r2 != 255 else -change_ratio if r < r2 and r2 > 0 else 0
    g2 += change_ratio if g > g2 and g2 != 255 else -change_ratio if g < g2 and g2 > 0 else 0
    b2 += change_ratio if b > b2 and b2 != 255 else -change_ratio if b < b2 and b2 > 0 else 0
    return (r2, g2, b2)

def update_frame(orignal_img, goal_img):
    length = len(orignal_img)
    change_ratio = 1
    for i in range(length):
        r, g, b = goal_img[i]
        r2, g2, b2 = orignal_img[i]

        orignal_img[i] = update_pixel(r, g, b, r2, g2, b2, change_ratio)
    
    return orignal_img

img1 = Image.open("./temp/somepic.jpg")
img2 = Image.open(second_img)

img1_data = list(img1.getdata())
img2_data = list(img2.getdata())

video = cv2.VideoWriter("./temp/output.avi", 0, 80, img1.size)

def write_video(frame):
    new_frame = Image.new("RGB", img1.size)
    new_frame.putdata(frame)

    # WRITE TO VIDEO
    frame = cv2.cvtColor(cv2.UMat(np.array(new_frame)), cv2.COLOR_RGB2BGR)
    video.write(frame)

write_video(img1_data)
write_video(img1_data)
write_video(img1_data)

async def create_frame_and_write_it_to_video():
    frame = update_frame(img1_data, img2_data)
    write_video(frame)

tasks = []

async def main():
    for _ in range(200):
        tasks.append(asyncio.create_task(create_frame_and_write_it_to_video()))

    await asyncio.gather(*tasks)


asyncio.run(main())
write_video(img2_data)

end = time.time()

print(f"PROGRAM TOOK {start - end} SECONDS TO RUN")

video.release()
cv2.destroyAllWindows()


def add_audio_to_video(video_file, audio_file, output_file):
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", video_file, "-i", audio_file,
            "-c:v", "copy", "-filter:a", "volume=20dB", "-c:a", "aac", "-strict", "experimental", output_file
        ], check=True)

        print(f"Audio added successfully: {output_file}")
        
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

    try:
        command = f"ffmpeg -y -i {output_file} -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 192k output.mp4"
        subprocess.run(command.split(), check=True)

        print(f"Audio added successfully: {output_file}")
        
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

video_file = "./temp/output.avi"
audio_file = "output_audio.mp3"
output_file = "./temp/output_video_with_audio.avi"


add_audio_to_video(video_file, audio_file, output_file)

for path in os.listdir("./temp"):
    os.remove("./temp/" + path)

print(f"-------------------------------------- PROGRAM TOOK {time.time() - start} SECONDS TO RUN --------------------------------------")