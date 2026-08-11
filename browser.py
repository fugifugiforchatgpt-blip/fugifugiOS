#!/usr/bin/env python3
"""
Полноценный браузер на Python (PyQt6 + Chromium-движок QWebEngine).

Возможности (по ТЗ):
- Открывает любые сайты (реальный рендеринг HTML/CSS/JS через Chromium)
- Несколько вкладок
- Адресная строка с автодополнением по истории набора
- Кнопки Назад / Вперёд / Обновить / Домой
- Загрузка файлов (простое сохранение без доп. интерфейса)
- Сохранение входа (аккаунт Google и другие сайты)
- Без закладок, без DevTools, без расширений

Установка зависимостей:
    pip install PyQt6 PyQt6-WebEngine

Запуск:
    python browser.py
"""

import sys
import os
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QToolBar,
    QLineEdit,
    QTabWidget,
    QTabBar,
    QWidget,
    QVBoxLayout,
    QCompleter,
    QFileDialog,
    QMessageBox,
    QStyle,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage

NEW_TAB_LABEL = "+"
HOME_URL = "https://www.google.com"


def normalize_url(text: str) -> QUrl:
    """Превращает введённый пользователем текст в корректный QUrl.
    Если это не похоже на URL — ищет через Google."""
    text = text.strip()
    if not text:
        return QUrl(HOME_URL)

    has_scheme = "://" in text
    looks_like_domain = (
        "." in text and " " not in text and not text.startswith(("http://", "https://"))
    )

    if has_scheme:
        url = QUrl(text)
    elif looks_like_domain:
        url = QUrl("https://" + text)
    else:
        # Не похоже на адрес сайта -> ищем в Google
        query = QUrl.toPercentEncoding(text).data().decode()
        url = QUrl(f"https://www.google.com/search?q={query}")

    if not url.isValid():
        query = QUrl.toPercentEncoding(text).data().decode()
        url = QUrl(f"https://www.google.com/search?q={query}")

    return url


class BrowserTab(QWidget):
    """Одна вкладка браузера с собственным WebEngineView."""

    def __init__(self, profile: QWebEngineProfile, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        page = QWebEnginePage(profile, self)
        self.view = QWebEngineView(self)
        self.view.setPage(page)

        layout.addWidget(self.view)
        self.setLayout(layout)

    def load(self, url: QUrl):
        self.view.load(url)

    def shutdown(self):
        """Корректно останавливает загрузку и освобождает ресурсы страницы,
        чтобы избежать краша GPU-процесса QtWebEngine при закрытии вкладки."""
        try:
            self.view.stop()
            page = self.view.page()
            self.view.setPage(None)
            if page is not None:
                page.deleteLater()
        except RuntimeError:
            # объект уже удалён Qt — ничего страшного
            pass


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FugiFugi Browser")
        self.resize(1280, 800)

        # ---- НАСТРОЙКА ПРОФИЛЯ (СОХРАНЕНИЕ ВХОДА) ----
        self.profile = QWebEngineProfile("FugiFugiProfile", self)
        self.profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 FugiFugiBrowser/1.0"
        )

        # Папка для данных браузера (куки, localStorage, пароли)
        data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_data")
        self.profile.setPersistentStoragePath(data_path)

        # Разрешаем постоянное сохранение кук (вход в Google и др.)
        self.profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
        )

        # Обработка загрузок
        self.profile.downloadRequested.connect(self.handle_download)

        # Вкладки
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_toolbar_for_current_tab)
        self.tabs.tabBarClicked.connect(self.on_tab_bar_clicked)
        self.setCentralWidget(self.tabs)

        # История введённых адресов (для автодополнения)
        self.typed_history = []

        self.build_toolbar()

        # Первая рабочая вкладка
        self.add_new_tab(QUrl(HOME_URL))
        # Служебная вкладка "+" всегда идёт последней
        self.add_plus_tab()

    # ---------- Тулбар ----------

    def build_toolbar(self):
        toolbar = QToolBar("Навигация")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        style = self.style()

        back_action = QAction(style.standardIcon(QStyle.StandardPixmap.SP_ArrowBack), "Назад", self)
        back_action.triggered.connect(lambda: self.current_view() and self.current_view().back())
        toolbar.addAction(back_action)

        forward_action = QAction(style.standardIcon(QStyle.StandardPixmap.SP_ArrowForward), "Вперёд", self)
        forward_action.triggered.connect(lambda: self.current_view() and self.current_view().forward())
        toolbar.addAction(forward_action)

        reload_action = QAction(style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload), "Обновить", self)
        reload_action.triggered.connect(lambda: self.current_view() and self.current_view().reload())
        toolbar.addAction(reload_action)

        home_action = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DirHomeIcon), "Домой", self)
        home_action.triggered.connect(lambda: self.navigate_current(QUrl(HOME_URL)))
        toolbar.addAction(home_action)

        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.navigate_from_address_bar)
        self.completer = QCompleter(self.typed_history)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.address_bar.setCompleter(self.completer)
        toolbar.addWidget(self.address_bar)

    # ---------- Вкладки ----------

    def plus_tab_index(self):
        last = self.tabs.count() - 1
        if last >= 0 and self.tabs.tabText(last) == NEW_TAB_LABEL:
            return last
        return -1

    def add_plus_tab(self):
        placeholder = QWidget()
        index = self.tabs.addTab(placeholder, NEW_TAB_LABEL)
        self.tabs.tabBar().setTabButton(index, QTabBar.ButtonPosition.RightSide, None)
        self.tabs.tabBar().setTabButton(index, QTabBar.ButtonPosition.LeftSide, None)
        return index

    def on_tab_bar_clicked(self, index):
        if self.tabs.tabText(index) == NEW_TAB_LABEL:
            self.add_new_tab(QUrl(HOME_URL))

    def add_new_tab(self, url: QUrl):
        tab = BrowserTab(self.profile, self)
        plus_index = self.plus_tab_index()
        if plus_index != -1:
            index = self.tabs.insertTab(plus_index, tab, "Новая вкладка")
        else:
            index = self.tabs.addTab(tab, "Новая вкладка")
        self.tabs.setCurrentIndex(index)

        tab.view.urlChanged.connect(lambda qurl, tab=tab: self.on_url_changed(tab, qurl))
        tab.view.titleChanged.connect(lambda title, tab=tab: self.on_title_changed(tab, title))
        tab.view.iconChanged.connect(lambda icon, tab=tab: self.on_icon_changed(tab, icon))

        tab.load(url)
        return tab

    def real_tab_count(self):
        count = self.tabs.count()
        if self.plus_tab_index() != -1:
            count -= 1
        return count

    def close_tab(self, index):
        if self.tabs.tabText(index) == NEW_TAB_LABEL:
            return
        if self.real_tab_count() <= 1:
            self.close()
            return

        widget = self.tabs.widget(index)
        if widget is None:
            return

        if self.tabs.currentIndex() == index:
            neighbor = index - 1 if index > 0 else index + 1
            if neighbor == self.plus_tab_index():
                neighbor = index - 1
            self.tabs.setCurrentIndex(max(neighbor, 0))

        self.tabs.removeTab(index)
        widget.setParent(None)
        widget.shutdown()
        QTimer.singleShot(0, widget.deleteLater)

    def current_tab(self) -> BrowserTab:
        widget = self.tabs.currentWidget()
        if isinstance(widget, BrowserTab):
            return widget
        return None

    def current_view(self) -> QWebEngineView:
        tab = self.current_tab()
        return tab.view if tab else None

    # ---------- Навигация ----------

    def navigate_from_address_bar(self):
        text = self.address_bar.text()
        url = normalize_url(text)
        if text and text not in self.typed_history:
            self.typed_history.append(text)
            self.completer.setModel(None)
            self.completer = QCompleter(self.typed_history)
            self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.address_bar.setCompleter(self.completer)
        self.navigate_current(url)

    def navigate_current(self, url: QUrl):
        view = self.current_view()
        if view:
            view.load(url)

    # ---------- Обновление UI ----------

    def on_url_changed(self, tab: BrowserTab, qurl: QUrl):
        if self.tabs.currentWidget() is tab:
            self.address_bar.setText(qurl.toString())
            self.address_bar.setCursorPosition(0)

    def on_title_changed(self, tab: BrowserTab, title: str):
        index = self.tabs.indexOf(tab)
        if index != -1:
            short_title = title if len(title) <= 20 else title[:20] + "…"
            self.tabs.setTabText(index, short_title or "Новая вкладка")

    def on_icon_changed(self, tab: BrowserTab, icon: QIcon):
        index = self.tabs.indexOf(tab)
        if index != -1:
            self.tabs.setTabIcon(index, icon)

    def update_toolbar_for_current_tab(self, index):
        view = self.current_view()
        if view:
            self.address_bar.setText(view.url().toString())

    # ---------- Загрузка файлов ----------

    def handle_download(self, download):
        suggested_name = download.downloadFileName() or "download"
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", suggested_name)
        if path:
            download.setDownloadDirectory(os.path.dirname(path))
            download.setDownloadFileName(os.path.basename(path))
            download.accept()
            download.isFinishedChanged.connect(
                lambda: QMessageBox.information(self, "Загрузка завершена", f"Файл сохранён:\n{path}")
                if download.isFinished()
                else None
            )
        else:
            download.cancel()


# ============================================================
#  ОБЁРТКА ДЛЯ ИНТЕГРАЦИИ В ОС FUGIFUGI
# ============================================================

class BrowserApp:
    """
    Обёртка для запуска браузера из ОС FugiFugi.
    Совместима с панелью задач и меню «Пуск».
    """
    def __init__(self, parent, taskbar):
        self.parent = parent
        self.taskbar = taskbar

        self.window = MainWindow(parent=parent)
        self.window.setWindowTitle("FugiFugi Browser")
        self.window.resize(1280, 800)

        self.taskbar.add_window(self.window, "FugiFugi Browser")

        self.window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.window.destroyed.connect(self.on_close)

        self.window.show()

    def on_close(self):
        try:
            self.taskbar.remove_window(self.window)
        except:
            pass


# ============================================================
#  ЗАПУСК (отладка отдельно от ОС)
# ============================================================

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("FugiFugi Browser")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()