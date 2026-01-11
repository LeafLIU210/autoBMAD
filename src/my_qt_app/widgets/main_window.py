"""
主窗口模块 - 使用PySide6实现

此模块定义了应用程序的主窗口界面，
采用现代Qt设计模式和最佳实践。
"""

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口标题
        self.setWindowTitle("PyQt Windows应用程序模板 v2.0")

        # 设置窗口大小
        self.setMinimumSize(800, 600)
        self.resize(800, 600)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建布局
        layout = QVBoxLayout(central_widget)

        # 添加欢迎标签
        welcome_label = QLabel("欢迎使用PyQt Windows应用程序模板")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(welcome_label)

        # 添加说明标签
        description_label = QLabel(
            "这是一个使用PySide6构建的现代Qt应用程序模板。\n"
            "项目集成了BMAD开发方法论和AI辅助开发工具。"
        )
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setFont(QFont("Arial", 10))
        description_label.setStyleSheet("color: gray;")
        layout.addWidget(description_label)

        # 添加测试按钮
        test_button = QPushButton("点击测试")
        test_button.clicked.connect(self.on_test_button_clicked)
        layout.addWidget(test_button)

        # 添加关闭按钮
        close_button = QPushButton("关闭应用")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        # 添加弹性空间
        layout.addStretch()

    def on_test_button_clicked(self):
        """测试按钮点击事件"""
        QMessageBox.information(
            self,
            "测试消息",
            "PySide6应用程序运行正常！\n\n"
            "这是一个使用PySide6构建的现代Qt应用程序。\n"
            "项目采用BMAD开发方法论和AI辅助开发。",
        )
