# wells.py
# Escala de Wells para Tromboembolismo Pulmonar (TEP)

from gi.repository import Gtk, Adw
import gettext

_ = gettext.gettext

class CalculadoraWells(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        # Contenedor con scroll para respetar la altura de la ventana (GTK 4)
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_vexpand(True)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.append(self.scroll)

        clamp = Adw.Clamp(
            maximum_size=600,
            margin_top=12,
            margin_bottom=24,
            margin_start=12,
            margin_end=12
        )
        self.scroll.set_child(clamp)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        clamp.set_child(box)

        # --- SECCIÓN DE CRITERIOS ---
        grupo_entrada = Adw.PreferencesGroup(
            title=_("Criterios Clínicos"),
            description=_("Seleccione los hallazgos presentes en el paciente.")
        )
        box.append(grupo_entrada)

        # Definición de criterios y sus puntajes
        self.criterios = [
            ("signos_tvp", _("Signos clínicos de TVP"), 3.0),
            ("diagnostico_alternativo", _("Diagnóstico alternativo menos probable que TEP"), 3.0),
            ("frecuencia_cardiaca", _("Frecuencia cardíaca > 100 lpm"), 1.5),
            ("inmovilizacion", _("Cirugía o inmovilización reciente (4 semanas)"), 1.5),
            ("ant_tvp_tep", _("Antecedentes de TVP o TEP"), 1.5),
            ("hemoptisis", _("Hemoptisis"), 1.0),
            ("cancer", _("Cáncer (en tratamiento o paliativo)"), 1.0)
        ]

        self.switches = {}
        for id_crit, label, puntos in self.criterios:
            fila = Adw.SwitchRow(title=label)
            # Guardamos el puntaje en el objeto para el cálculo
            fila.puntos = puntos
            grupo_entrada.add(fila)
            self.switches[id_crit] = fila

        # --- SECCIÓN DE RESULTADO ---
        grupo_resultado = Adw.PreferencesGroup(title=_("Probabilidad Clínica"))
        box.append(grupo_resultado)

        caja_res = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, css_classes=["card"])
        caja_res.set_margin_top(12)

        self.label_puntos = Gtk.Label(label="0", css_classes=["title-1", "accent"])
        self.label_unidad = Gtk.Label(label=_("puntos"), css_classes=["caption", "dim-label"])

        caja_res.append(self.label_puntos)
        caja_res.append(self.label_unidad)
        grupo_resultado.add(caja_res)

        self.fila_interpretacion = Adw.ActionRow(
            title=_("Interpretación (Modelo simplificado)"),
            subtitle=_("TEP poco probable")
        )
        grupo_resultado.add(self.fila_interpretacion)

        # Botón de cálculo
        boton = Gtk.Button(
            label=_("Calcular Score"),
            margin_top=12,
            css_classes=["suggested-action", "pill"]
        )
        boton.set_margin_start(90)
        boton.set_margin_end(90)
        boton.connect("clicked", self.calcular)
        box.append(boton)

    def calcular(self, boton):
        total = 0.0
        for fila in self.switches.values():
            if fila.get_active():
                total += fila.puntos

        self.label_puntos.set_label(f"{total:g}".replace('.', ','))

        # Interpretación (Criterios de Wells simplificados/dicotómicos)
        if total > 4.0:
            nivel = _("TEP probable")
            color = "error"
        else:
            nivel = _("TEP poco probable")
            color = "success"

        self.fila_interpretacion.set_subtitle(nivel)

        # Feedback visual en el número
        self.label_puntos.remove_css_class("success")
        self.label_puntos.remove_css_class("error")
        self.label_puntos.add_css_class(color)
