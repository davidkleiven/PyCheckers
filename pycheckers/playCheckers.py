import gui as pychgui
import game as gm

def main():
    app = pychgui.PyCheckerGUI()
    app.game.p1.setHumanUser()
    app.game.p1.name = "David Kleiven"
    app.game.p2.name = "Computer"
    app.play()

if __name__ == "__main__":
    main()
