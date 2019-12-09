import threading
def threadTest():
    print("The Thread!")

def test1():
    print("Hello")
    t=threading.Thread(group=None,target=threadTest,name="Porkins")
    t.start()

