from PyQt6.QtWidgets import (QWidget, QLabel, QSlider, QDoubleSpinBox,
                             QRadioButton, QButtonGroup, QVBoxLayout, QHBoxLayout, QCheckBox)
from PyQt6.QtCore import Qt
import logging
from gui.update_depth_label import update_depth_label
from gui.shortcuts_dialog import show_shortcuts_dialog

logger = logging.getLogger(__name__)

# Reusable style constants
_FONT = "'Segoe UI', sans-serif"

def _radio_style(app):
    return f"""
        QRadioButton {{
            background-color: {app.surface_color};
            color: {app.text_color};
            font-family: {_FONT};
            font-size: 10pt;
            padding-top: 0px;
            padding-bottom: 0px;
            padding-left: 10px;
            padding-right: 10px;
            border-radius: 6px;
            border: 1px solid {app.border_color};
            min-height: 40px;
        }}
        QRadioButton:hover {{
            background-color: #253555;
            border-color: {app.accent_color};
        }}
        QRadioButton:checked {{
            border-color: {app.accent_color};
            background-color: rgba(124, 58, 237, 0.15);
        }}
        QRadioButton::indicator {{
            width: 14px;
            height: 14px;
        }}
    """

def _section_label(app, text):
    lbl = QLabel(text)
    lbl.setStyleSheet(f"""
        color: {app.muted_color};
        font-family: {_FONT};
        font-size: 10pt;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    """)
    return lbl

def _slider_style(app):
    return f"""
        QSlider::groove:horizontal {{
            background: {app.surface_color};
            height: 6px;
            border-radius: 3px;
        }}
        QSlider::sub-page:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #7c3aed, stop:1 #a78bfa);
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #a78bfa, stop:1 #7c3aed);
            width: 18px;
            height: 18px;
            margin: -6px 0;
            border-radius: 9px;
            border: 2px solid {app.bg_color};
        }}
        QSlider::handle:horizontal:hover {{
            background: #a78bfa;
        }}
    """


def create_widgets(app):
    central_widget = QWidget()
    app.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)

    # ── Color Selection Screen ──────────────────────────────
    app.color_frame = QWidget()
    app.color_frame.setObjectName("colorFrame")
    app.color_frame.setStyleSheet(f"QWidget#colorFrame {{ background-color: {app.bg_color}; }}")
    color_layout = QVBoxLayout(app.color_frame)
    color_layout.setContentsMargins(20, 20, 20, 20)

    # Title — centered
    header = QLabel("RAMURI")
    header.setStyleSheet(f"""
        color: {app.accent_color};
        font-family: {_FONT};
        font-size: 22pt;
        font-weight: bold;
        letter-spacing: 3px;
    """)
    header.setAlignment(Qt.AlignmentFlag.AlignCenter)
    color_layout.addWidget(header)

    subtitle = QLabel("Chess Assistant")
    subtitle.setStyleSheet(f"""
        color: {app.muted_color};
        font-family: {_FONT};
        font-size: 9pt;
        letter-spacing: 1px;
    """)
    subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
    color_layout.addWidget(subtitle)

    # Shortcuts button — right aligned
    shortcuts_row = QWidget()
    shortcuts_h = QHBoxLayout(shortcuts_row)
    shortcuts_h.setContentsMargins(0, 5, 0, 0)
    app.shortcuts_btn = app.create_shortcuts_button(shortcuts_row, lambda: show_shortcuts_dialog(app))
    shortcuts_h.addStretch()
    shortcuts_h.addWidget(app.shortcuts_btn)
    color_layout.addWidget(shortcuts_row)
    color_layout.addSpacing(12)

    # Color panel card
    color_panel = QWidget()
    color_panel.setObjectName("colorPanel")
    color_panel.setStyleSheet(f"""
        QWidget#colorPanel {{
            background-color: {app.frame_color};
            border-radius: 12px;
            border: 1px solid {app.border_color};
        }}
    """)
    cp_layout = QVBoxLayout(color_panel)
    cp_layout.setContentsMargins(24, 24, 24, 24)

    color_label = QLabel("Select Your Color")
    color_label.setStyleSheet(f"color: {app.text_color}; font-family: {_FONT}; font-size: 13pt; font-weight: 600;")
    color_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cp_layout.addWidget(color_label)
    cp_layout.addSpacing(12)

    # White / Black buttons
    btn_frame = QWidget()
    btn_h = QHBoxLayout(btn_frame)
    btn_h.setContentsMargins(0, 0, 0, 0)
    btn_h.setSpacing(12)
    app.btn_white = app.create_color_button(btn_frame, "White", "w")
    app.btn_black = app.create_color_button(btn_frame, "Black", "b")
    btn_h.addWidget(app.btn_white)
    btn_h.addWidget(app.btn_black)
    cp_layout.addWidget(btn_frame)
    cp_layout.addSpacing(20)

    # ── Depth slider (color screen) ──
    cp_layout.addWidget(_section_label(app, "Engine Depth"))
    cp_layout.addSpacing(6)

    app.depth_slider = QSlider(Qt.Orientation.Horizontal)
    app.depth_slider.setMinimum(10)
    app.depth_slider.setMaximum(30)
    app.depth_slider.setValue(app.depth_var)
    app.depth_slider.setStyleSheet(_slider_style(app))
    cp_layout.addWidget(app.depth_slider)
    cp_layout.addSpacing(4)

    app.depth_label = QLabel(f"Depth: {app.depth_var}")
    app.depth_label.setStyleSheet(f"color: {app.text_color}; font-family: {_FONT}; font-size: 10pt;")
    app.depth_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    cp_layout.addWidget(app.depth_label)
    cp_layout.addSpacing(16)

    # ── Screenshot delay ──
    cp_layout.addWidget(_section_label(app, "Screenshot Delay"))
    cp_layout.addSpacing(6)

    app.delay_spinbox = QDoubleSpinBox()
    app.delay_spinbox.setMinimum(0.0)
    app.delay_spinbox.setMaximum(1)
    app.delay_spinbox.setSingleStep(0.1)
    app.delay_spinbox.setValue(app.screenshot_delay_var)
    app.delay_spinbox.setDecimals(1)
    app.delay_spinbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
    app.delay_spinbox.setFixedWidth(100)
    app.delay_spinbox.setFixedHeight(34)
    app.delay_spinbox.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.UpDownArrows)
    app.delay_spinbox.setStyleSheet(f"""
        QDoubleSpinBox {{
            background-color: {app.surface_color};
            color: {app.text_color};
            border: 1px solid {app.border_color};
            border-radius: 8px;
            padding: 5px 20px 5px 5px;
            font-family: {_FONT};
            font-size: 10pt;
        }}
        QDoubleSpinBox::up-button {{
            subcontrol-origin: border; subcontrol-position: top right;
            width: 18px; height: 16px;
            background-color: {app.accent_color};
            border-top-right-radius: 7px;
            border-left: 1px solid {app.border_color};
        }}
        QDoubleSpinBox::down-button {{
            subcontrol-origin: border; subcontrol-position: bottom right;
            width: 18px; height: 16px;
            background-color: {app.accent_color};
            border-bottom-right-radius: 7px;
            border-left: 1px solid {app.border_color};
        }}
        QDoubleSpinBox::up-button:hover {{ background-color: {app.hover_color}; }}
        QDoubleSpinBox::down-button:hover {{ background-color: {app.hover_color}; }}
        QDoubleSpinBox::up-arrow {{
            image: none; width: 0; height: 0;
            border-left: 4px solid transparent; border-right: 4px solid transparent;
            border-bottom: 5px solid {app.text_color}; margin: 0 5px;
        }}
        QDoubleSpinBox::down-arrow {{
            image: none; width: 0; height: 0;
            border-left: 4px solid transparent; border-right: 4px solid transparent;
            border-top: 5px solid {app.text_color}; margin: 0 5px;
        }}
    """)
    app.delay_spinbox.valueChanged.connect(lambda val: setattr(app, 'screenshot_delay_var', val))
    cp_layout.addWidget(app.delay_spinbox)
    cp_layout.addSpacing(16)

    # ── Move mode (color screen) ──
    cp_layout.addWidget(_section_label(app, "Move Mode"))
    cp_layout.addSpacing(6)

    app.move_mode_group = QButtonGroup()
    radio_h = QHBoxLayout()
    radio_h.setContentsMargins(0, 0, 0, 0)
    radio_h.setSpacing(12)

    drag_radio = QRadioButton("Drag")
    drag_radio.setChecked(True)
    drag_radio.setStyleSheet(_radio_style(app))
    drag_radio.toggled.connect(lambda checked: app.set_move_mode("drag") if checked else None)
    app.move_mode_group.addButton(drag_radio)
    radio_h.addWidget(drag_radio)

    click_radio = QRadioButton("Click")
    click_radio.setStyleSheet(_radio_style(app))
    click_radio.toggled.connect(lambda checked: app.set_move_mode("click") if checked else None)
    app.move_mode_group.addButton(click_radio)
    radio_h.addWidget(click_radio)

    cp_layout.addLayout(radio_h)

    color_layout.addWidget(color_panel)
    color_layout.addStretch()

    # ── Main Game Screen ────────────────────────────────────
    app.main_frame = QWidget()
    app.main_frame.setObjectName("mainFrame")
    app.main_frame.setStyleSheet(f"QWidget#mainFrame {{ background-color: {app.bg_color}; }}")
    mf_layout = QVBoxLayout(app.main_frame)
    mf_layout.setContentsMargins(20, 20, 20, 20)

    # Control card
    ctrl = QWidget()
    ctrl.setObjectName("ctrlPanel")
    ctrl.setStyleSheet(f"""
        QWidget#ctrlPanel {{
            background-color: {app.frame_color};
            border-radius: 12px;
            border: 1px solid {app.border_color};
        }}
    """)
    ctrl_layout = QVBoxLayout(ctrl)
    ctrl_layout.setContentsMargins(20, 20, 20, 20)

    # Play button
    app.btn_play = app.create_action_button(ctrl, "Play Next Move", app.process_move_thread)
    ctrl_layout.addWidget(app.btn_play)
    ctrl_layout.addSpacing(12)

    # Castling
    app.castling_frame = QWidget()
    cast_layout = QVBoxLayout(app.castling_frame)
    cast_layout.setContentsMargins(0, 0, 0, 0)
    cast_layout.setSpacing(8)

    cast_layout.addWidget(_section_label(app, "Castling Rights"))

    app.create_castling_checkboxes()
    cast_layout.addWidget(app.kingside_check)
    cast_layout.addWidget(app.queenside_check)
    ctrl_layout.addWidget(app.castling_frame)
    ctrl_layout.addSpacing(12)

    # Auto mode
    app.auto_mode_check = QCheckBox("Auto Next Moves")
    app.auto_mode_check.setStyleSheet(f"""
        QCheckBox {{
            background-color: {app.surface_color};
            color: {app.text_color};
            font-family: {_FONT};
            font-size: 11pt;
            font-weight: 500;
            padding-top: 0px;
            padding-bottom: 0px;
            padding-left: 10px;
            padding-right: 10px;
            border-radius: 8px;
            border: 1px solid {app.border_color};
            min-height: 44px;
        }}
        QCheckBox:hover {{
            background-color: #253555;
            border-color: {app.accent_color};
        }}
        QCheckBox::indicator {{ width: 18px; height: 18px; }}
    """)
    app.auto_mode_check.stateChanged.connect(
        lambda state: (setattr(app, 'auto_mode_var', state == Qt.CheckState.Checked.value), app.toggle_auto_mode())
    )
    ctrl_layout.addWidget(app.auto_mode_check, alignment=Qt.AlignmentFlag.AlignCenter)
    ctrl_layout.addSpacing(12)

    # Status label
    app.status_label = QLabel("")
    app.status_label.setStyleSheet(f"""
        color: {app.text_color};
        font-family: 'Consolas', 'Segoe UI', monospace;
        font-size: 10pt;
        background-color: {app.surface_color};
        padding: 12px;
        border-radius: 8px;
        border: 1px solid {app.border_color};
    """)
    app.status_label.setWordWrap(True)
    app.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    ctrl_layout.addWidget(app.status_label)
    ctrl_layout.addSpacing(12)

    # Depth slider (main screen)
    ctrl_layout.addWidget(_section_label(app, "Engine Depth"))
    ctrl_layout.addSpacing(6)

    app.depth_slider_main = QSlider(Qt.Orientation.Horizontal)
    app.depth_slider_main.setMinimum(10)
    app.depth_slider_main.setMaximum(30)
    app.depth_slider_main.setValue(app.depth_var)
    app.depth_slider_main.setStyleSheet(_slider_style(app))
    ctrl_layout.addWidget(app.depth_slider_main)
    ctrl_layout.addSpacing(4)

    app.depth_label_main = QLabel(f"Depth: {app.depth_var}")
    app.depth_label_main.setStyleSheet(f"color: {app.text_color}; font-family: {_FONT}; font-size: 10pt;")
    app.depth_label_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
    ctrl_layout.addWidget(app.depth_label_main)
    ctrl_layout.addSpacing(12)

    # Move mode (main screen)
    ctrl_layout.addWidget(_section_label(app, "Move Mode"))
    ctrl_layout.addSpacing(6)

    app.move_mode_group_main = QButtonGroup()
    radio_h2 = QHBoxLayout()
    radio_h2.setContentsMargins(0, 0, 0, 0)
    radio_h2.setSpacing(12)

    drag_radio_main = QRadioButton("Drag")
    drag_radio_main.setChecked(app.move_mode == "drag")
    drag_radio_main.setStyleSheet(_radio_style(app))
    drag_radio_main.toggled.connect(lambda checked: app.set_move_mode("drag") if checked else None)
    app.move_mode_group_main.addButton(drag_radio_main)
    radio_h2.addWidget(drag_radio_main)

    click_radio_main = QRadioButton("Click")
    click_radio_main.setChecked(app.move_mode == "click")
    click_radio_main.setStyleSheet(_radio_style(app))
    click_radio_main.toggled.connect(lambda checked: app.set_move_mode("click") if checked else None)
    app.move_mode_group_main.addButton(click_radio_main)
    radio_h2.addWidget(click_radio_main)

    ctrl_layout.addLayout(radio_h2)

    mf_layout.addWidget(ctrl)
    mf_layout.addStretch()

    main_layout.addWidget(app.color_frame)
    main_layout.addWidget(app.main_frame)

    app.color_frame.show()
    app.main_frame.hide()

    # Sync depth sliders
    def sync_depth_sliders(value):
        app.depth_slider.blockSignals(True)
        app.depth_slider_main.blockSignals(True)
        app.depth_slider.setValue(value)
        app.depth_slider_main.setValue(value)
        app.depth_slider.blockSignals(False)
        app.depth_slider_main.blockSignals(False)
        update_depth_label(app, value)
        app.depth_label_main.setText(f"Depth: {value}")

    app.depth_slider.valueChanged.connect(sync_depth_sliders)
    app.depth_slider_main.valueChanged.connect(sync_depth_sliders)
    app.btn_play.setEnabled(False)
    logger.debug("Widgets created successfully")