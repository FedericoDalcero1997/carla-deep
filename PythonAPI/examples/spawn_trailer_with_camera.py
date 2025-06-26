# spawn_trailer_with_camera.py
import cv2
import datetime
import glob
import numpy as np
import os
import pathlib
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import random

def process_and_save_image(image, output_dir):
    # Save non processed image
    image.save_to_disk(str(output_dir / f'camera_{image.frame:06d}.png'))

    # Convert raw buffer to RGB image
    img_array = np.frombuffer(image.raw_data, dtype=np.uint8)
    img_array = img_array.reshape((image.height, image.width, 4))  # BGRA
    rgb_image = img_array[:, :, :3]  # Keep only RGB

    # Gray scale
    gray = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)

    # Edge detection with Canny
    edges = cv2.Canny(gray, 100, 200)

    # Show processed image
    cv2.imshow("Edges", edges)
    cv2.waitKey(1)

def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    world = client.get_world()
    blueprint_library = world.get_blueprint_library()

    # Find the trailer blueprint (lowercase only!)
    trailer_bp = blueprint_library.find("vehicle.trailer.trailer")
    # Choose a spawn point
    spawn_points = world.get_map().get_spawn_points()
    trailer_spawn = spawn_points[0]  # pick a safe one

    # Spawn the trailer
    trailer = world.try_spawn_actor(trailer_bp, trailer_spawn)
    if trailer is None:
        print("Failed to spawn trailer.")
    else:
        print("Trailer spawned.")

    # Define camera similar to Onsemi AR0233
    camera_bp = blueprint_library.find('sensor.camera.rgb')
    camera_bp.set_attribute('image_size_x', '1920')
    camera_bp.set_attribute('image_size_y', '1208')
    camera_bp.set_attribute('fov', '120')  # Wide-angle lens
    camera_bp.set_attribute('sensor_tick', '0.033')  # ~30 FPS

    # Camera transform: front of the trailer, facing frontward
    camera_transform = carla.Transform(
        carla.Location(x=2.0, z=2.5),
        carla.Rotation(pitch=-10.0, yaw=0.0, roll=0.0)
    )

    # Spawn the camera sensor attached to the trailer
    camera = world.spawn_actor(camera_bp, camera_transform, attach_to=trailer)

    # Create output directory with date-time subfolder
    base_output_dir = pathlib.Path(__file__).resolve().parent.parent.parent / 'output'
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    run_output_dir = base_output_dir / timestamp
    run_output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Saving images to: {run_output_dir}")

    camera.listen(lambda image: process_and_save_image(image, run_output_dir))

    print("Camera attached to trailer and recording.")

    try:
        while True:
            world.wait_for_tick()
    except KeyboardInterrupt:
        print("Interrupted. Cleaning up...")
    finally:
        camera.stop()
        camera.destroy()
        trailer.destroy()
        print("Cleaned up actors.")

if __name__ == '__main__':
    main()
