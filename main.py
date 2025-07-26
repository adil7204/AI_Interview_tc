import sys
import os
from PyQt5.QtWidgets import QApplication, QStackedWidget
from pages import Page1, Page2, Page4

# This will delete previous session's answers
answer_file = "datafiles/answer_papers/all_answers.txt"
if os.path.exists(answer_file):
    with open(answer_file, "w", encoding="utf-8") as f:
        f.write("")  # Empty the file

class MainApp(QStackedWidget):
    def __init__(self):
        print("started mainapp")
        super().__init__()
        self.page1 = Page1(self.show_page2)
        self.page2 = Page2(self.show_page1, self.exit_app, self.show_result_page)
        self.page4 = Page4(self.show_page1, self.exit_app)

        self.addWidget(self.page1)
        self.addWidget(self.page2)
        self.addWidget(self.page4)
        
        self.setWindowTitle("TechMiya Self-Assessment")
        self.showMaximized()


    def show_page1(self):
        self.setCurrentWidget(self.page1)


    def show_page2(self):
        self.setCurrentWidget(self.page2)


    def show_page3(self, questions):
        self.page3 = Page3(self.show_page2, self.exit_app, self.show_result_page)
        self.addWidget(self.page3)
        self.setCurrentWidget(self.page3)
        self.page3.start_reading(questions)


    def show_page4(self):
        self.page4.load_results()
        self.setCurrentWidget(self.page4)


    def show_result_page(self):
        self.page4 = Page4(self.show_page1, self.exit_app)
        self.addWidget(self.page4)
        self.setCurrentWidget(self.page4)
        self.page4.load_results()


    def exit_app(self):
        QApplication.quit()


if __name__ == "__main__":
    print("Starting Project!!!")
    app = QApplication(sys.argv)
    window = MainApp()
    sys.exit(app.exec_())
