import pygame, asyncio
from src import game

async def main(game):
    while game.running:
        game.run()
        await asyncio.sleep(0)
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main(game.Game()))