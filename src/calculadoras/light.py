# light.py
# Criterios de Light para análisis de líquido pleural - ClinicalAyudante

from gi.repository import Gtk, Adw
import gettext
import locale

_ = gettext.gettext

class CalculadoraLight(Gtk.Box):
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

        # --- SECCIÓN DE ENTRADA: PROTEÍNAS ---
        grupo_proteinas = Adw.PreferencesGroup(
            title=_("1. Proteínas"),
            description=_("Relación de proteínas entre líquido pleural y suero.")
        )
        box.append(grupo_proteinas)

        self.prot_liquido = Adw.EntryRow(title=_("Proteínas en Líquido (g/dL)"))
        self.prot_suero = Adw.EntryRow(title=_("Proteínas en Suero (g/dL)"))

        grupo_proteinas.add(self.prot_liquido)
        grupo_proteinas.add(self.prot_suero)

        # --- SECCIÓN DE ENTRADA: LDH ---
        grupo_ldh = Adw.PreferencesGroup(
            title=_("2. LDH (Lactato Deshidrogenasa)"),
            description=_("Valores de LDH y límite superior normal (LSN) del suero.")
        )
        box.append(grupo_ldh)

        self.ldh_liquido = Adw.EntryRow(title=_("LDH en Líquido (U/L)"))
        self.ldh_suero = Adw.EntryRow(title=_("LDH en Suero (U/L)"))
        self.ldh_lsn = Adw.EntryRow(title=_("LSN LDH Suero (U/L)"))

        grupo_ldh.add(self.ldh_liquido)
        grupo_ldh.add(self.ldh_suero)
        grupo_ldh.add(self.ldh_lsn)

        # --- SECCIÓN DE RESULTADO ---
        grupo_res = Adw.PreferencesGroup(title=_("Interpretación"))
        box.append(grupo_res)

        caja_res = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, css_classes=["card"])
        caja_res.set_margin_top(12)

        self.label_tipo = Gtk.Label(label=_("Esperando datos..."), css_classes=["title-3", "accent"])
        self.label_detalles = Gtk.Label(label="", css_classes=["caption", "dim-label"])

        caja_res.append(self.label_tipo)
        caja_res.append(self.label_detalles)
        grupo_res.add(caja_res)

        # Botón estilo Pill consistente con curb65.py e imc.py
        boton = Gtk.Button(
            label=_("Evaluar Criterios"),
            margin_top=12,
            css_classes=["suggested-action", "pill"]
        )
        boton.set_margin_start(90)
        boton.set_margin_end(90)
        boton.connect("clicked", self.calcular)
        box.append(boton)

    def calcular(self, boton):
        try:
            # Procesamiento de texto (soporte para , y .)
            p_liq = float(self.prot_liquido.get_text().replace(',', '.'))
            p_ser = float(self.prot_suero.get_text().replace(',', '.'))
            l_liq = float(self.ldh_liquido.get_text().replace(',', '.'))
            l_ser = float(self.ldh_suero.get_text().replace(',', '.'))
            l_lsn = float(self.ldh_lsn.get_text().replace(',', '.'))

            # Cálculos de relaciones
            rel_prot = p_liq / p_ser
            rel_ldh = l_liq / l_ser
            ldh_lsn_ratio = l_liq / l_lsn

            # Evaluación de Criterios de Light (Exudado si cumple al menos uno)
            es_exudado = (rel_prot > 0.5) or (rel_ldh > 0.6) or (ldh_lsn_ratio > (2/3))

            if es_exudado:
                self.label_tipo.set_label(_("EXUDADO"))
                self.label_tipo.add_css_class("error")
                self.label_tipo.remove_css_class("success")
            else:
                self.label_tipo.set_label(_("TRASUDADO"))
                self.label_tipo.add_css_class("success")
                self.label_tipo.remove_css_class("error")

            # Mostrar ratios calculados según LOCALE
            rp_str = locale.format_string("%.2f", rel_prot)
            rl_str = locale.format_string("%.2f", rel_ldh)
            self.label_detalles.set_label(f"Rel. Prot: {rp_str} | Rel. LDH: {rl_str}")

        except (ValueError, ZeroDivisionError):
            self.label_tipo.set_label(_("Error"))
            self.label_detalles.set_label(_("Verifique los valores de entrada"))
