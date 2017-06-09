import gui as pychgui
import game as gm

def main():
    app = pychgui.PyCheckerGUI()
    app.game.p1.setHumanUser()
    app.play()

if __name__ == "__main__":
    main()
