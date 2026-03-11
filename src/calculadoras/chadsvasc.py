# chadsvasc.py
# Escala CHA2DS2-VASc para riesgo de ACV - ClinicalAyudante

from gi.repository import Gtk, Adw
import gettext

_ = gettext.gettext

class CalculadoraChadsvasc(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_vexpand(True)
        self.append(self.scroll)

        clamp = Adw.Clamp(maximum_size=600, margin_top=12, margin_bottom=24)
        self.scroll.set_child(clamp)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        clamp.set_child(box)

        # --- SECCIÓN DE CRITERIOS ---
        grupo = Adw.PreferencesGroup(title=_("Factores de Riesgo"))
        box.append(grupo)

        # Diccionario con (Título, Puntos)
        self.items = {
            "c": Adw.SwitchRow(title=_("Insuficiencia Cardíaca Congestiva")),
            "h": Adw.SwitchRow(title=_("Hipertensión")),
            "a2": Adw.SwitchRow(title=_("Edad ≥ 75 años"), subtitle=_("Suma 2 puntos")),
            "d": Adw.SwitchRow(title=_("Diabetes Mellitus")),
            "s2": Adw.SwitchRow(title=_("ACV / AIT / Tromboembolismo previo"), subtitle=_("Suma 2 puntos")),
            "v": Adw.SwitchRow(title=_("Enfermedad Vascular (IAM, EVP o Placa aórtica)")),
            "a1": Adw.SwitchRow(title=_("Edad 65-74 años")),
            "sc": Adw.SwitchRow(title=_("Categoría de Sexo (Femenino)"))
        }

        for fila in self.items.values():
            grupo.add(fila)

        # --- RESULTADO ---
        grupo_res = Adw.PreferencesGroup(title=_("Puntuación Total"))
        box.append(grupo_res)

        self.label_puntos = Gtk.Label(label="0", css_classes=["title-1", "accent"])
        grupo_res.add(self.label_puntos)

        self.fila_recom = Adw.ActionRow(title=_("Recomendación"))
        grupo_res.add(self.fila_recom)

        boton = Gtk.Button(label=_("Calcular"), css_classes=["suggested-action", "pill"])
        boton.set_margin_start(90); boton.set_margin_end(90); boton.set_margin_top(12)
        boton.connect("clicked", self.calcular)
        box.append(boton)

    def calcular(self, boton):
        puntos = 0
        puntos += 1 if self.items["c"].get_active() else 0
        puntos += 1 if self.items["h"].get_active() else 0
        puntos += 2 if self.items["a2"].get_active() else 0
        puntos += 1 if self.items["d"].get_active() else 0
        puntos += 2 if self.items["s2"].get_active() else 0
        puntos += 1 if self.items["v"].get_active() else 0
        puntos += 1 if self.items["a1"].get_active() else 0
        puntos += 1 if self.items["sc"].get_active() else 0

        self.label_puntos.set_label(str(puntos))

        # Recomendación simplificada
        if puntos == 0:
            rec = _("No requiere anticoagulación")
        elif puntos == 1:
            rec = _("Considerar anticoagulación (según sexo)")
        else:
            rec = _("Anticoagulación recomendada")

        self.fila_recom.set_subtitle(rec)
