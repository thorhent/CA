# ckd_epi.py
# Calculadora de Tasa de Filtración Glomerular (CKD-EPI 2021)

from gi.repository import Gtk, Adw
import gettext

_ = gettext.gettext

class CalculadoraCKDEPI(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        # Mantenemos el Clamp para un ancho máximo elegante de 600px
        clamp = Adw.Clamp(
            maximum_size=600,
            margin_top=12,  # Ajustado según tu preferencia
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
            title=_("Parámetros Renales"),
            description=_("Fórmula CKD-EPI 2021.")
        )
        box.append(grupo_entrada)

        # Creatinina
        self.fila_crea = Adw.EntryRow(title=_("Creatinina Sérica"))
        self.fila_crea.add_suffix(Gtk.Label(label="mg/dL", css_classes=["dim-label"]))
        grupo_entrada.add(self.fila_crea)

        # Edad
        self.fila_edad = Adw.EntryRow(title=_("Edad"))
        self.fila_edad.add_suffix(Gtk.Label(label=_("años"), css_classes=["dim-label"]))
        grupo_entrada.add(self.fila_edad)

        # Sexo
        self.fila_sexo = Adw.ComboRow(
            title=_("Sexo"),
            model=Gtk.StringList.new([_("Femenino"), _("Masculino")])
        )
        grupo_entrada.add(self.fila_sexo)

        # --- SECCIÓN DE RESULTADO ---
        grupo_resultado = Adw.PreferencesGroup(title=_("Resultado eGFR"))
        box.append(grupo_resultado)

        caja_res = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, css_classes=["card"])
        caja_res.set_margin_top(12) # Ajustado según tu preferencia

        self.label_egfr = Gtk.Label(label="--", css_classes=["title-1", "accent"])
        self.label_unidad = Gtk.Label(
            label="mL/min/1.73 m²",
            css_classes=["caption", "dim-label"]
        )

        caja_res.append(self.label_egfr)
        caja_res.append(self.label_unidad)
        grupo_resultado.add(caja_res)

        # Botón de cálculo
        boton = Gtk.Button(
            label=_("Calcular eGFR"),
            margin_top=12, # Ajustado según tu preferencia
            css_classes=["suggested-action", "pill"]
        )
        boton.set_margin_start(90)
        boton.set_margin_end(90)
        boton.connect("clicked", self.calcular)
        box.append(boton)

    def calcular(self, boton):
        try:
            # Soporte para coma decimal regional
            crea_text = self.fila_crea.get_text().replace(',', '.')
            edad_text = self.fila_edad.get_text().replace(',', '.')

            if not crea_text or not edad_text:
                return

            crea = float(crea_text)
            edad = float(edad_text)
            es_masculino = self.fila_sexo.get_selected() == 1

            # Constantes CKD-EPI 2021
            kappa = 0.9 if es_masculino else 0.7
            alfa = -0.412 if es_masculino else -0.241
            c_sexo = 1.0 if es_masculino else 1.012

            # Cálculo
            e_crea_min = min(crea / kappa, 1) ** alfa
            e_crea_max = max(crea / kappa, 1) ** -1.2
            e_edad = 0.9938 ** edad

            egfr = 142 * e_crea_min * e_crea_max * e_edad * c_sexo

            # Mostrar resultado con formato local
            self.label_egfr.set_label(f"{egfr:.0f}")

        except (ValueError, ZeroDivisionError):
            self.label_egfr.set_label("--")
