# curb65.py
# Escala CURB-65 para Severidad de Neumonía

from gi.repository import Gtk, Adw
import gettext

_ = gettext.gettext

class CalculadoraCurb65(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        # Contenedor con scroll para respetar la altura de la ventana en GTK 4
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
            title=_("Criterios CURB-65"),
            description=_("Marque los hallazgos presentes para evaluar la severidad.")
        )
        box.append(grupo_entrada)

        # Definición de los 5 criterios (1 punto cada uno)
        self.criterios = [
            ("confusion", _("Confusión"), _("Desorientación en persona, tiempo o espacio")),
            ("urea", _("Urea > 7 mmol/L"), _("BUN > 19 mg/dL")),
            ("respiratoria", _("Frecuencia Respiratoria ≥ 30 rpm"), None),
            ("presion", _("PAS &lt; 90 mmHg o PAD ≤ 60 mmHg"), _("Hipotensión arterial")),
            ("edad", _("Edad ≥ 65 años"), None)
        ]

        self.switches = {}
        for id_crit, titulo, subtitulo in self.criterios:
            fila = Adw.SwitchRow(title=titulo)
            if subtitulo:
                fila.set_subtitle(subtitulo)
            grupo_entrada.add(fila)
            self.switches[id_crit] = fila

        # --- SECCIÓN DE RESULTADO ---
        grupo_resultado = Adw.PreferencesGroup(title=_("Puntaje y Mortalidad"))
        box.append(grupo_resultado)

        caja_res = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, css_classes=["card"])
        caja_res.set_margin_top(12)

        self.label_puntos = Gtk.Label(label="0", css_classes=["title-1", "accent"])
        self.label_unidad = Gtk.Label(label=_("puntos"), css_classes=["caption", "dim-label"])

        caja_res.append(self.label_puntos)
        caja_res.append(self.label_unidad)
        grupo_resultado.add(caja_res)

        self.fila_interpretacion = Adw.ActionRow(
            title=_("Recomendación Clínica"),
            subtitle=_("Tratamiento ambulatorio sugerido")
        )
        grupo_resultado.add(self.fila_interpretacion)

        # Botón de cálculo con estilo pill y márgenes laterales de 90
        boton = Gtk.Button(
            label=_("Calcular CURB-65"),
            margin_top=12,
            css_classes=["suggested-action", "pill"]
        )
        boton.set_margin_start(90)
        boton.set_margin_end(90)
        boton.connect("clicked", self.calcular)
        box.append(boton)

    def calcular(self, boton):
        total = 0
        for fila in self.switches.values():
            if fila.get_active():
                total += 1

        self.label_puntos.set_label(str(total))

        # Interpretación basada en el puntaje total
        if total <= 1:
            nivel = _("Riesgo bajo: Tratamiento ambulatorio")
            color = "success"
        elif total == 2:
            nivel = _("Riesgo moderado: Considerar ingreso hospitalario")
            color = "warning"
        else:
            nivel = _("Riesgo alto: Ingreso urgente (valorar UCI)")
            color = "error"

        self.fila_interpretacion.set_subtitle(nivel)

        # Feedback visual mediante clases de color de Libadwaita
        for c in ["success", "warning", "error"]:
            self.label_puntos.remove_css_class(c)
        self.label_puntos.add_css_class(color)
