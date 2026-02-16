# Vista de Configuracion - todos los tabs definidos en el .ui

import os
from PyQt5.QtWidgets import QWidget, QTabWidget
from PyQt5 import uic
from app.config.catalogos import CATALOGO_CONFIGS
from app.views.catalogo_list_widget import CatalogoListWidget
from app.views.geografia_widget import GeografiaWidget

UI_PATH = os.path.join(os.path.dirname(__file__), "ui", "configuracion", "configuracion_view.ui")


class ConfiguracionView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(UI_PATH, self)
        self._catalog_widgets = {}
        self._setup_ui()

    def _setup_ui(self):
        # insertar un CatalogoListWidget en cada sub-tab del .ui
        for key, config in CATALOGO_CONFIGS.items():
            tab_layout_name = config.get('tab_layout')
            layout = getattr(self, tab_layout_name, None)
            if layout is None:
                continue

            widget = CatalogoListWidget(config)
            self._catalog_widgets[key] = widget
            layout.addWidget(widget)

        # insertar el widget de geografia en su tab
        geo_widget = GeografiaWidget()
        self._catalog_widgets['__geografia__'] = geo_widget
        self.tabGeografiaLayout.addWidget(geo_widget)

        # conectar senales de cambio de tabs para cargar datos
        self.categoriasTabs.currentChanged.connect(self._on_category_tab_changed)

        # conectar sub-tabs
        for sub_tab_name in ['ventasSubTabs', 'actividadesSubTabs',
                             'contactosSubTabs', 'finanzasSubTabs']:
            sub_tab = getattr(self, sub_tab_name, None)
            if sub_tab and isinstance(sub_tab, QTabWidget):
                sub_tab.currentChanged.connect(
                    lambda idx, w=sub_tab: self._on_subtab_changed(w, idx)
                )

        # cargar datos del primer tab
        if self.categoriasTabs.count() > 0:
            self._on_category_tab_changed(0)

    def _on_category_tab_changed(self, index):
        widget = self.categoriasTabs.widget(index)
        if not widget:
            return

        # buscar si es el tab de geografia
        if widget.objectName() == 'tabGeografia':
            geo = self._catalog_widgets.get('__geografia__')
            if geo:
                geo.cargar_datos()
            return

        # buscar el sub-tab widget dentro del tab
        sub_tab = widget.findChild(QTabWidget)
        if sub_tab:
            self._on_subtab_changed(sub_tab, sub_tab.currentIndex())

    def _on_subtab_changed(self, sub_tab_widget, sub_index):
        widget = sub_tab_widget.widget(sub_index)
        if isinstance(widget, QWidget):
            # buscar el CatalogoListWidget dentro del widget del sub-tab
            catalog_widget = widget.findChild(CatalogoListWidget)
            if catalog_widget:
                catalog_widget.cargar_datos()
