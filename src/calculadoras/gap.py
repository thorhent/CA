# gap.py
# Calculadora de Brecha Aniónica (Anion Gap) para ClinicalAyudante

from gi.repository import Gtk, Adw
import gettext

_ = gettext.gettext

class CalculadoraGap(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        # Contenedor Clamp para un ancho máximo elegante de 600px
        clamp = Adw.Clamp(
            maximum_size=600,
            margin_top=12,
            margin_bottom=24,
            margin_start=12,
            margin_end=12
        )
        self.append(clamp)

        # Usamos spacing=8 para una densidad visual intermedia
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        clamp.set_child(box)

        # --- SECCIÓN DE ENTRADA ---
        grupo_entrada = Adw.PreferencesGroup(
            title=_("Electrolitos Séricos"),
            description=_("Ingrese los valores en mEq/L para calcular la brecha aniónica.")
        )
        box.append(grupo_entrada)

        # Sodio (Na+)
        self.fila_na = Adw.EntryRow(title=_("Sodio (Na+)"))
        self.fila_na.add_suffix(Gtk.Label(label="mEq/L", css_classes=["dim-label"]))
        grupo_entrada.add(self.fila_na)

        # Cloro (Cl-)
        self.fila_cl = Adw.EntryRow(title=_("Cloro (Cl-)"))
        self.fila_cl.add_suffix(Gtk.Label(label="mEq/L", css_classes=["dim-label"]))
        grupo_entrada.add(self.fila_cl)

        # Bicarbonato (HCO3-)
        self.fila_hco3 = Adw.EntryRow(title=_("Bicarbonato (HCO3-)"))
        self.fila_hco3.add_suffix(Gtk.Label(label="mEq/L", css_classes=["dim-label"]))
        grupo_entrada.add(self.fila_hco3)

        # --- SECCIÓN DE RESULTADO ---
        grupo_resultado = Adw.PreferencesGroup(title=_("Resultado Anion Gap"))
        box.append(grupo_resultado)

        caja_res = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, css_classes=["card"])
        caja_res.set_margin_top(12)

        self.label_gap = Gtk.Label(label="--", css_classes=["title-1", "accent"])
        self.label_unidad = Gtk.Label(
            label="mEq/L",
            css_classes=["caption", "dim-label"]
        )

        caja_res.append(self.label_gap)
        caja_res.append(self.label_unidad)
        grupo_resultado.add(caja_res)

        # Botón de cálculo con márgenes laterales para diseño "pill"
        boton = Gtk.Button(
            label=_("Calcular Gap"),
            margin_top=12,
            css_classes=["suggested-action", "pill"]
        )
        boton.set_margin_start(90)
        boton.set_margin_end(90)
        boton.connect("clicked", self.calcular)
        box.append(boton)

    def calcular(self, boton):
        try:
            # Soporte para coma decimal regional
            na_text = self.fila_na.get_text().replace(',', '.')
            cl_text = self.fila_cl.get_text().replace(',', '.')
            hco3_text = self.fila_hco3.get_text().replace(',', '.')

            if not na_text or not cl_text or not hco3_text:
                return

            na = float(na_text)
            cl = float(cl_text)
            hco3 = float(hco3_text)

            # Fórmula: Anion Gap = Na - (Cl + HCO3)
            gap = na - (cl + hco3)

            # Mostrar resultado con formato local
            self.label_gap.set_label(f"{gap:.1f}".replace('.', ','))

        except (ValueError, ZeroDivisionError):
            self.label_gap.set_label("--")
