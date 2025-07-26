from PyQt5.QtWidgets import QPushButton

def apply_button_style(button: QPushButton, background_color: str = "#0074D9"):  # Blue
    button.setStyleSheet(f"""
        QPushButton {{
            font-size: 16px;
            min-width: 160px;
            min-height: 40px;
            background-color: {background_color};
            color: white;
            border: none;
            border-radius: 0px; /* Square corners */
            font-weight: bold;
            background-image: none; /* Remove background image if inherited */
        }}
        QPushButton:hover {{
            background-color: orange;
            color: white;
        }}
        QPushButton:pressed {{
            background-color: #005299;
            color: white;
        }}
    """)
