# gold.py
# Clasificación GOLD 2024 para EPOC - ClinicalAyudante
# Soporte para decimales (, o .) y formato según LOCALE

from gi.repository import Gtk, Adw
import gettext
import locale

_ = gettext.gettext

class CalculadoraGold(Gtk.Box):
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

        # --- SECCIÓN 1: ESPIROMETRÍA ---
        grupo_espiro = Adw.PreferencesGroup(
            title=_("1. Limitación del Flujo Aéreo"),
            description=_("Ingrese los valores observados y previstos (L).")
        )
        box.append(grupo_espiro)

        self.vef1_obs = Adw.EntryRow(title=_("VEF1 Observado (L)"))
        self.vef1_obs.set_input_purpose(Gtk.InputPurpose.NUMBER)
        grupo_espiro.add(self.vef1_obs)

        self.vef1_prev = Adw.EntryRow(title=_("VEF1 Previsto (L)"))
        self.vef1_prev.set_input_purpose(Gtk.InputPurpose.NUMBER)
        grupo_espiro.add(self.vef1_prev)

        self.fila_porcentaje = Adw.ActionRow(title=_("Porcentaje Calculado"))
        self.label_porcentaje = Gtk.Label(label="--,-%", css_classes=["title-3", "dim-label"])
        self.fila_porcentaje.add_suffix(self.label_porcentaje)
        grupo_espiro.add(self.fila_porcentaje)

        # --- SECCIÓN 2: EVALUACIÓN CLÍNICA (ABE) ---
        grupo_clinico = Adw.PreferencesGroup(title=_("2. Evaluación Clínica (ABE)"))
        box.append(grupo_clinico)

        self.mmrc_row = Adw.ComboRow(
            title=_("Síntomas (mMRC / CAT)"),
            model=Gtk.StringList.new([_("Pocos (0-1 / <10)"), _("Muchos (≥2 / ≥10)")])
        )
        grupo_clinico.add(self.mmrc_row)

        self.exac_row = Adw.ComboRow(
            title=_("Historial de Exacerbaciones"),
            model=Gtk.StringList.new([_("0-1 (Sin hospitalización)"), _("≥2 o ≥1 hospitalización")])
        )
        grupo_clinico.add(self.exac_row)

        # --- RESULTADOS ---
        grupo_res = Adw.PreferencesGroup(title=_("Resultado Final"))
        box.append(grupo_res)

        self.res_grado = Adw.ActionRow(title=_("Grado Espirométrico (1-4)"))
        self.label_grado = Gtk.Label(label="-", css_classes=["title-1", "accent"])
        self.res_grado.add_suffix(self.label_grado)
        grupo_res.add(self.res_grado)

        self.res_grupo = Adw.ActionRow(title=_("Grupo Clínico (A, B, E)"))
        self.label_grupo = Gtk.Label(label="-", css_classes=["title-1", "accent"])
        self.res_grupo.add_suffix(self.label_grupo)
        grupo_res.add(self.res_grupo)

        boton_calc = Gtk.Button(
            label=_("Clasificar GOLD"),
            margin_top=18,
            css_classes=["suggested-action", "pill"]
        )
        boton_calc.set_margin_start(90)
        boton_calc.set_margin_end(90)
        boton_calc.connect("clicked", self.ejecutar_calculo)
        box.append(boton_calc)

    def ejecutar_calculo(self, boton):
        try:
            # Procesamiento flexible: permite ',' o '.' convirtiendo a flotante estándar
            t_obs = self.vef1_obs.get_text().replace(',', '.')
            t_prev = self.vef1_prev.get_text().replace(',', '.')

            if not t_obs or not t_prev: return

            obs = float(t_obs)
            prev = float(t_prev)

            if prev > 0:
                porcentaje = (obs / prev) * 100

                # Formateo según el LOCALE del sistema (respeta coma o punto decimal)
                # Ejemplo: 75,5% en es/pt o 75.5% en en
                formato_local = locale.format_string("%.1f", porcentaje)
                self.label_porcentaje.set_label(f"{formato_local}%")

                # Clasificación 1-4
                if porcentaje >= 80: grado = "1"
                elif porcentaje >= 50: grado = "2"
                elif porcentaje >= 30: grado = "3"
                else: grado = "4"
                self.label_grado.set_label(grado)

        except (ValueError, ZeroDivisionError):
            self.label_porcentaje.set_label(_("Error"))

        # Clasificación ABE
        m_alto = self.mmrc_row.get_selected() == 1
        e_alto = self.exac_row.get_selected() == 1

        if e_alto: grupo = "E"
        elif m_alto: grupo = "B"
        else: grupo = "A"

        self.label_grupo.set_label(grupo)
