# spawn_trailer.py
import glob
import os
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

if __name__ == '__main__':
    main()
