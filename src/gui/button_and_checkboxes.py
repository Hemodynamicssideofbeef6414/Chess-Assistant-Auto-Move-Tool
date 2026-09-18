from PyQt6.QtWidgets import QPushButton, QCheckBox
from PyQt6.QtCore import Qt
import logging

logger = logging.getLogger(__name__)

_FONT = "'Segoe UI', sans-serif"

def color_button(app, parent, text, color):
    btn = QPushButton(text, parent)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {app.accent_color};
            color: {app.text_color};
            border: none;
            border-radius: 10px;
            font-family: {_FONT};
            font-size: 11pt;
            font-weight: bold;
            padding-top: 0px;
            padding-bottom: 0px;
            padding-left: 15px;
            padding-right: 15px;
            min-height: 48px;
        }}
        QPushButton:hover {{
            background-color: {app.hover_color};
        }}
        QPushButton:pressed {{
            background-color: #5b21b6;
        }}
    """)
    btn.clicked.connect(lambda: app.set_color(color))
    return btn

def action_button(app, parent, text, command):
    btn = QPushButton(text, parent)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #7c3aed, stop:1 #6366f1);
            color: {app.text_color};
            border: none;
            border-radius: 10px;
            font-family: {_FONT};
            font-size: 12pt;
            font-weight: bold;
            padding-top: 0px;
            padding-bottom: 0px;
            padding-left: 15px;
            padding-right: 15px;
            min-height: 52px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #6d28d9, stop:1 #4f46e5);
        }}
        QPushButton:pressed {{
            background: #5b21b6;
        }}
        QPushButton:disabled {{
            background: {app.surface_color};
            color: {app.muted_color};
            border: 1px solid {app.border_color};
        }}
    """)
    btn.clicked.connect(command)
    return btn

def shortcuts_button(app, parent, command):
    btn = QPushButton("Keys", parent)
    btn.setFixedWidth(60)
    btn.setMinimumHeight(28)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {app.surface_color};
            color: {app.muted_color};
            border: 1px solid {app.border_color};
            border-radius: 6px;
            font-family: {_FONT};
            font-size: 9pt;
            padding: 4px;
        }}
        QPushButton:hover {{
            background-color: #253555;
            border-color: {app.accent_color};
            color: {app.text_color};
        }}
        QPushButton:pressed {{
            background-color: {app.frame_color};
        }}
    """)
    btn.clicked.connect(command)
    return btn

def castling_checkboxes(app):
    logger.debug("Creating castling checkboxes")

    style = f"""
        QCheckBox {{
            background-color: {app.surface_color};
            color: {app.text_color};
            font-family: {_FONT};
            font-size: 10pt;
            padding-top: 0px;
            padding-bottom: 0px;
            padding-left: 8px;
            padding-right: 8px;
            border-radius: 6px;
            border: 1px solid {app.border_color};
            min-height: 40px;
        }}
        QCheckBox:hover {{
            background-color: #253555;
            border-color: {app.accent_color};
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
        }}
    """

    kingside_check = QCheckBox("Kingside Castle", app.castling_frame)
    kingside_check.setStyleSheet(style)
    kingside_check.stateChanged.connect(lambda state: setattr(app, 'kingside_var', state == Qt.CheckState.Checked.value))
    app.kingside_check = kingside_check
    app.kingside_var = False

    queenside_check = QCheckBox("Queenside Castle", app.castling_frame)
    queenside_check.setStyleSheet(style)
    queenside_check.stateChanged.connect(lambda state: setattr(app, 'queenside_var', state == Qt.CheckState.Checked.value))
    app.queenside_check = queenside_check
    app.queenside_var = False

def move_mode(app, parent, text, method):
    btn = QPushButton(text, parent)
    btn.setFixedWidth(100)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {app.accent_color};
            color: {app.text_color};
            border: none;
            border-radius: 8px;
            font-family: {_FONT};
            font-size: 10pt;
            font-weight: 600;
            padding-top: 0px;
            padding-bottom: 0px;
            min-height: 40px;
        }}
        QPushButton:hover {{
            background-color: {app.hover_color};
        }}
        QPushButton:pressed {{
            background-color: #5b21b6;
        }}
    """)
    btn.clicked.connect(lambda: app.set_move_mode(method))
    return btn
