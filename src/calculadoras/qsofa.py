# qsofa.py
# Escala Quick SOFA para evaluación de Sepsis - ClinicalAyudante

from gi.repository import Gtk, Adw
import gettext

_ = gettext.gettext

class CalculadoraQsofa(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

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
            title=_("Criterios qSOFA"),
            description=_("Evaluación rápida de disfunción de órganos.")
        )
        box.append(grupo_entrada)

        self.criterios = {
            "estado": Adw.SwitchRow(title=_("Alteración del estado mental"), subtitle=_("Glasgow &lt; 15")),
            "presion": Adw.SwitchRow(title=_("Hipotensión sistólica"), subtitle=_("PAS ≤ 100 mmHg")),
            "frecuencia": Adw.SwitchRow(title=_("Taquipnea"), subtitle=_("FR ≥ 22 rpm"))
        }

        for fila in self.criterios.values():
            grupo_entrada.add(fila)

        # --- SECCIÓN DE RESULTADO ---
        grupo_resultado = Adw.PreferencesGroup(title=_("Resultado"))
        box.append(grupo_resultado)

        caja_res = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, css_classes=["card"])
        caja_res.set_margin_top(12)

        self.label_puntos = Gtk.Label(label="0", css_classes=["title-1", "accent"])
        self.label_desc = Gtk.Label(label=_("Bajo riesgo"), css_classes=["caption", "dim-label"])

        caja_res.append(self.label_puntos)
        caja_res.append(self.label_desc)
        grupo_resultado.add(caja_res)

        boton = Gtk.Button(
            label=_("Evaluar qSOFA"),
            margin_top=12,
            css_classes=["suggested-action", "pill"]
        )
        boton.set_margin_start(90)
        boton.set_margin_end(90)
        boton.connect("clicked", self.calcular)
        box.append(boton)

    def calcular(self, boton):
        total = sum(1 for f in self.criterios.values() if f.get_active())
        self.label_puntos.set_label(str(total))

        if total >= 2:
            self.label_desc.set_label(_("Alto riesgo de mortalidad o estancia prolongada en UCI"))
            self.label_puntos.add_css_class("error")
        else:
            self.label_desc.set_label(_("Bajo riesgo"))
            self.label_puntos.remove_css_class("error")
