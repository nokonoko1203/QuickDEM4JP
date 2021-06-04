# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Contents
                                 A QGIS plugin
 The plugin to convert DEM to GeoTiff and Terrain RGB (Tiff).
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-05-31
        git sha              : $Format:%H$
        copyright            : (C) 2021 by MIERUNE Inc.
        email                : info@mierune.co.jp
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import xml.etree.ElementTree as et

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import *
from qgis.gui import *

from .quick_dem_for_jp_dialog import QuickDEMforJPDialog
from .convert_fgd_dem.converter import Converter


class Contents:
    def __init__(self, iface):
        self.iface = iface
        self.dlg = QuickDEMforJPDialog()
        self.current_dir = os.path.dirname(os.path.abspath(__file__))

        self.dlg.mQgsFileWidget_inputPath.setFilePath(self.current_dir)
        self.dlg.mQgsFileWidget_inputPath.setFilter("*.xml;;*.zip")
        self.dlg.mQgsFileWidget_outputPath.setFilePath(self.current_dir)
        self.dlg.mQgsProjectionSelectionWidget_outputCrs.setCrs(QgsProject.instance().crs())

        input_type = {
            'zip or xml': 1,
            'folder': 2,
        }
        for key in input_type:
            self.dlg.comboBox_inputType.addItem(key, input_type[key])
        self.dlg.comboBox_inputType.activated.connect(self.switch_input_type)

        self.dlg.button_box.accepted.connect(self.convert_DEM)
        self.dlg.button_box.rejected.connect(self.dlg_cancel)

    def convert(self, rgbify):
        converter = Converter(
            import_path=self.import_path,
            output_path=self.geotiff_output_path,
            output_epsg=self.output_epsg,
            rgbify=rgbify
        )
        converter.dem_to_geotiff()

    def add_layer(self, tiff_name, layer_name):
        layer = QgsRasterLayer(os.path.join(self.geotiff_output_path, tiff_name), layer_name)
        QgsProject.instance().addMapLayer(layer) 

    def convert_DEM(self):
        do_GeoTiff = self.dlg.checkBox_outputGeoTiff.isChecked()
        do_TerrainRGB = self.dlg.checkBox_outputTerrainRGB.isChecked()
        do_add_layer = self.dlg.checkBox_openLayers.isChecked()

        if not do_GeoTiff and not do_TerrainRGB:
            QMessageBox.information(None, 'エラー', u'出力形式にチェックを入れてください')
            return

        self.import_path = self.dlg.mQgsFileWidget_inputPath.filePath()
        self.geotiff_output_path = self.dlg.mQgsFileWidget_outputPath.filePath()
        self.output_epsg = self.dlg.mQgsProjectionSelectionWidget_outputCrs.crs().authid()

        try:
            if do_GeoTiff:
                self.convert(rgbify=False)
                if do_add_layer:
                    self.add_layer('output.tif', 'output')
            if do_TerrainRGB:
                self.convert(rgbify=True)
                if do_add_layer:
                    self.add_layer('rgbify.tif', 'rgbify')
        except (ValueError, AttributeError, et.ParseError):
            QMessageBox.information(None, 'エラー', u'処理中にエラーが発生しました。DEMが正しいか確認してください')
            return
        except Exception as e:
            QMessageBox.information(None, 'エラー', f'{e}')
            return

        QMessageBox.information(None, '完了', u'処理が完了しました')
        self.dlg.hide()

        return True

    def dlg_cancel(self):
        self.dlg.hide()

    def switch_input_type(self):
        if self.dlg.comboBox_inputType.currentData() == 1:
            self.dlg.mQgsFileWidget_inputPath.setStorageMode(QgsFileWidget.GetMultipleFiles)
        else:
            self.dlg.mQgsFileWidget_inputPath.setStorageMode(QgsFileWidget.GetDirectory)

