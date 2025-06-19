from bot import Bot


if __name__ == "__main__":
    try:
        brain = Bot()
    except Exception as e:
        print(str(e))
        exit(-1)

    brain.run()
