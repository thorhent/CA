# window.py
#
# Copyright 2025 Taylan Branco Meurer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

from gi.repository import Adw, Gtk, GLib
from .conectar import Connect
from collections import Counter
import math
import gettext

_ = gettext.gettext

@Gtk.Template(resource_path='/io/github/thorhent/CA/window.ui')
class ClinicalayudanteWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'ClinicalayudanteWindow'

    entrySintomas = Gtk.Template.Child("entrySintomas")
    butAddSintomas = Gtk.Template.Child("butAddSintomas")
    adwExpandSintomas = Gtk.Template.Child("adwExpandSintomas")
    butRemSintomas = Gtk.Template.Child("butRemSintomas")
    enfermedadesListBox = Gtk.Template.Child("enfermedadesListBox")
    labelPosiblesEnfermedades = Gtk.Template.Child("labelPosiblesEnfermedades")
    tov = Gtk.Template.Child("tov")

    ICONOS_LISTA = (
        "network-cellular-signal-excellent-rtl-symbolic",
        "network-cellular-signal-good-rtl-symbolic",
        "network-cellular-signal-ok-rtl-symbolic",
        "network-cellular-signal-weak-rtl-symbolic",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.labelList = []
        self.getListaBDSignosSintomas()

    def getListaBDSignosSintomas(self):
        try:
            conn = Connect()
            cursor = conn.conectar()
            sintomas = cursor.execute(
                "SELECT DISTINCT sintoma_signo FROM clinica ORDER BY sintoma_signo ASC;"
            ).fetchall()

            completion = Gtk.EntryCompletion()
            list_store = Gtk.ListStore.new([str])
            for sintoma in sintomas:
                list_store.append(sintoma)

            completion.set_model(list_store)
            completion.set_text_column(0)
            completion.set_inline_completion(True)
            completion.set_inline_selection(True)
            self.entrySintomas.set_completion(completion)

        except Exception as e:
            print(e)
            toast = Adw.Toast(title=_("Falla en la conexión inicial con base de datos."))
            self.tov.add_toast(toast)

    def _agregar_sintoma(self, texto):
        if not texto.strip():
            return
        label = Gtk.Label(label=texto)
        self.labelList.append(label)
        self.adwExpandSintomas.add_row(label)
        self.entrySintomas.set_text("")
        self.entrySintomas.grab_focus_without_selecting()

    @Gtk.Template.Callback("entrySintomas_enter")
    def enter_add_sintomas(self, *args):
        self._agregar_sintoma(self.entrySintomas.get_text())

    @Gtk.Template.Callback("butAddSintomas_clicked")
    def add_sintomas(self, *args):
        self._agregar_sintoma(self.entrySintomas.get_text())

    @Gtk.Template.Callback("butRemSintomas_clicked")
    def quit_sintomas(self, *args):
        if self.labelList:
            self.adwExpandSintomas.remove(self.labelList[-1].get_parent())
            self.labelList.pop()

    @Gtk.Template.Callback("butLimpiar_clicked")
    def limpiar_sintomas(self, *args):
        for hijo in self.labelList:
            self.adwExpandSintomas.remove(hijo.get_parent())
        self.labelList.clear()

    @Gtk.Template.Callback("butInvestigar_clicked")
    def investigar_enfermedades(self, *args):
        if not self.labelList:
            toast = Adw.Toast(title=_("Agregue síntomas o signos."))
            self.tov.add_toast(toast)
            return

        conn = Connect()
        cursor = conn.conectar()
        condiciones = " OR ".join(
            "sintoma_signo = ?" for _ in self.labelList
        )
        query = f"""
            SELECT clinica.*, enfermedades.enfermedad, enfermedades.síndrome
            FROM clinica
            INNER JOIN enfermedades USING(cod_enfermedad)
            WHERE {condiciones};
        """
        valores = [label.get_text() for label in self.labelList]
        datos = cursor.execute(query, valores).fetchall()

        lista_ordenada = self.ordenar_enfermedades(datos)
        self.escribir_enfermedades(lista_ordenada)
        #self.labelPosiblesEnfermedades.set_label(f"Posibles enfermedades [{len(lista_ordenada)}]")
        self.labelPosiblesEnfermedades.set_label(_("Posibles enfermedades [{}]").format(len(lista_ordenada)))

    def ordenar_enfermedades(self, listaDatos):
        enfermedades = [(row[3], row[4]) for row in listaDatos]
        contador = Counter(enfermedades)
        listaEAQ = [(enf, sind, cnt) for (enf, sind), cnt in contador.items()]
        return sorted(listaEAQ, key=lambda x: x[2], reverse=True)

    def escribir_enfermedades(self, listaNova):
        self.enfermedadesListBox.remove_all()
        total = len(self.labelList)
        for enfermedad, sindrome, match in listaNova:
            ratio = match / total
            if ratio == 1:
                icon = self.ICONOS_LISTA[0]
            elif ratio >= 0.6:
                icon = self.ICONOS_LISTA[1]
            elif ratio > 0.4:
                icon = self.ICONOS_LISTA[2]
            else:
                icon = self.ICONOS_LISTA[3]
            self.crear_adwActions(enfermedad, sindrome, icon)

    def crear_adwActions(self, enfermedad, sindrome, icon):
        adwAction = Adw.ActionRow()
        adwAction.set_title(enfermedad)
        sindrome = sindrome or ""
        adwAction.set_subtitle(sindrome)
        adwAction.set_icon_name(icon)
        adwAction.set_margin_top(5)
        adwAction.set_margin_start(10)
        adwAction.set_margin_end(10)
        adwAction.set_margin_bottom(5)

        boton = Gtk.Button()
        boton.set_name(enfermedad)
        boton.set_icon_name("edit-copy-symbolic")
        boton.set_margin_top(10)
        boton.set_margin_start(20)
        boton.set_margin_bottom(10)

        adwAction.add_suffix(boton)
        self.enfermedadesListBox.append(adwAction)
        boton.connect("clicked", self.on_clicked)
        GLib.idle_add(adwAction.activate)

    def on_clicked(self, boton):
        builder = Gtk.Builder()
        builder.add_from_resource('/io/github/thorhent/CA/enfermedad_window.ui')
        ventana_enfermedad = builder.get_object("enfermedad_window")
        ventana_enfermedad.set_title(boton.get_name())

        listBoxTratFarmacologico = builder.get_object("listBoxTratFarmacologico")
        gridSS = builder.get_object("gridSS")
        listBoxPreguntasP1 = builder.get_object("listBoxPreguntasP1")
        listBoxExploracion = builder.get_object("listBoxExploracion")
        listBoxEstudios = builder.get_object("listBoxEstudios")
        statusPage1 = builder.get_object("statusPage1")
        statusPage2 = builder.get_object("statusPage2")
        statusPage3 = builder.get_object("statusPage3")
        statusPage4 = builder.get_object("statusPage4")

        conn = Connect()
        cursor = conn.conectar()
        cod_enfermedad = cursor.execute(
            "SELECT cod_enfermedad FROM enfermedades WHERE enfermedad = ?;",
            (boton.get_name(),)
        ).fetchone()

        datosTratamiento = cursor.execute(
            "SELECT * FROM tratamientos WHERE cod_enfermedad = ?;", cod_enfermedad
        ).fetchall()
        datosSS = cursor.execute(
            "SELECT DISTINCT sintoma_signo FROM clinica WHERE cod_enfermedad = ?;", cod_enfermedad
        ).fetchall()
        datosPreguntas = cursor.execute(
            "SELECT * FROM preguntas WHERE cod_enfermedad = ? ORDER BY cod_pregunta ASC;", cod_enfermedad
        ).fetchall()
        datosExploracion = cursor.execute(
            "SELECT * FROM exploraciones_fisicas WHERE cod_enfermedad = ?;", cod_enfermedad
        ).fetchall()
        datosEstudios = cursor.execute(
            "SELECT * FROM estudios WHERE cod_enfermedad = ?;", cod_enfermedad
        ).fetchall()

        for sp in (statusPage1, statusPage2, statusPage3, statusPage4):
            sp.set_description(boton.get_name())

        self.crear_tratamiento(datosTratamiento, listBoxTratFarmacologico)
        self.crear_anamnesis(datosSS, datosPreguntas, gridSS, listBoxPreguntasP1)
        self.crear_estudios(datosEstudios, listBoxEstudios)
        self.crear_exploracion_fisica(datosExploracion, listBoxExploracion)

        ventana_enfermedad.present()

    def crear_anamnesis(self, datos, datosPreguntas, gridSS, listBoxPreguntasP1):
        lineas = math.ceil(len(datos) / 4)
        aux = 0
        for linea in range(lineas):
            for columna in range(4):
                if aux == len(datos):
                    break
                adwAction = Adw.ActionRow()
                adwAction.set_title(datos[aux][0])
                adwAction.set_margin_top(5)
                adwAction.set_margin_start(10)
                adwAction.set_margin_end(10)
                adwAction.set_margin_bottom(5)
                adwAction.add_css_class("card")
                gridSS.attach(adwAction, columna, linea, 1, 1)
                aux += 1

        for dato in datosPreguntas:
            adwAction = Adw.ActionRow()
            adwAction.set_title(dato[2])
            adwAction.set_margin_top(5)
            adwAction.set_margin_start(10)
            adwAction.set_margin_end(10)
            adwAction.set_margin_bottom(5)
            listBoxPreguntasP1.append(adwAction)

    def crear_exploracion_fisica(self, datos, listBoxExploracion):
        if not datos:
            return
        titulos = ["Inspección", "Palpación", "Percusión", "Auscultación"]
        for idx, titulo in enumerate(titulos, start=2):
            if datos[0][idx]:
                lista = datos[0][idx].split("; ")
                expander = Adw.ExpanderRow()
                expander.set_title(f"<b>{titulo}</b>")
                expander.set_use_markup(True)
                expander.set_margin_top(5)
                expander.set_margin_start(10)
                expander.set_margin_end(10)
                expander.set_margin_bottom(5)
                for item in lista:
                    row = Adw.ActionRow()
                    row.set_title(item)
                    row.set_margin_start(25)
                    row.set_margin_end(25)
                    expander.add_row(row)
                listBoxExploracion.append(expander)

    def crear_estudios(self, datos, listBoxEstudios):
        for dato in datos:
            objetivos = dato[4].split("; ")
            expander = Adw.ExpanderRow()
            expander.set_title(f"<b>{dato[3]}</b>")
            expander.set_use_markup(True)
            expander.set_subtitle(f"Estudio: {dato[2]}")
            for objetivo in objetivos:
                row = Adw.ActionRow()
                row.set_title(objetivo)
                row.set_margin_start(25)
                row.set_margin_end(25)
                expander.add_row(row)
            expander.set_margin_top(5)
            expander.set_margin_start(10)
            expander.set_margin_end(10)
            expander.set_margin_bottom(5)
            listBoxEstudios.append(expander)

    def crear_tratamiento(self, datos, listBoxTratFarmacologico):
        for dato in datos:
            expander = Adw.ExpanderRow()
            expander.set_margin_top(5)
            expander.set_margin_start(10)
            expander.set_margin_end(10)
            expander.set_margin_bottom(5)
            expander.set_title(f"<b>{dato[4]}</b>")
            expander.set_use_markup(True)
            expander.set_subtitle(f"<b>Clase:</b> {dato[3]}   <b>Tipo:</b> {dato[2]}")
            expander.set_use_markup(True)
            objetivo = Adw.ActionRow()
            objetivo.set_title("Objetivo")
            objetivo.set_subtitle(dato[5])
            objetivo.set_margin_start(25)
            objetivo.set_margin_end(25)
            expander.add_row(objetivo)
            if dato[6]:
                otros = Adw.ActionRow()
                otros.set_title(_("Otras informaciones"))
                otros.set_subtitle(dato[6])
                otros.set_margin_start(25)
                otros.set_margin_end(25)
                expander.add_row(otros)
            listBoxTratFarmacologico.append(expander)

